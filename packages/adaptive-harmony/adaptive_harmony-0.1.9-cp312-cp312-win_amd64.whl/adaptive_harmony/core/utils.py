import asyncio
import functools
import itertools
import json
import linecache
import numpy as np
import random

from loguru import logger
from pathlib import Path
from rich.progress import Progress, TaskID
from tqdm.auto import tqdm
from typing import Callable, Iterator, Iterable, TypedDict, NamedTuple, List, Dict, Any, Coroutine, TypeVar

from adaptive_harmony import InferenceModel, TrainingModel, StringThread


async def gather_with_auto_tqdm(*aws, **tqdm_kwargs):
    """
    Gather multiple awaitables with automatic progress bar tracking.

    This function wraps asyncio.gather() with a tqdm progress bar to show progress
    of multiple concurrent tasks. It ensures the progress bar is properly updated
    and closed even if some tasks fail.

    Args:
        *aws: Variable number of awaitable objects to gather
        **tqdm_kwargs: Additional keyword arguments to pass to tqdm constructor

    Returns:
        List of results from all awaitables in the same order as input

    Note:
        The progress bar will be automatically closed even if an exception occurs
        during task execution.
    """
    pbar = tqdm(total=len(aws), **tqdm_kwargs)

    async def wrapper(aw, pbar_instance):
        try:
            return await aw
        finally:
            if pbar_instance.n < pbar_instance.total:
                pbar_instance.update(1)

    wrapped_tasks = [wrapper(aw, pbar) for aw in aws]

    try:
        results = await asyncio.gather(*wrapped_tasks)
    finally:
        pbar.close()

    return results


S = TypeVar("S")
T = TypeVar("T")


class InnerProgress:

    def __init__(self, on_start, on_complete):
        self.current_step = 0
        self.on_start = on_start
        self.on_complete = on_complete
        self.last_str = None

    def start(self, str):

        self.on_start(self.current_step, str if str != self.last_str else "")
        self.processing = self.current_step + 1
        self.last_str = str

    def done(self):
        self.current_step = self.processing
        self.on_complete()


class MultiProgressTracker:
    def __init__(self, pbar: Progress):
        self.all: list[InnerProgress] = []
        self.progress_tasks: list[TaskID] = []
        self.pbar = pbar

    def new_progress(self):
        prog = InnerProgress(self.start, self.update)
        self.all.append(prog)
        return prog

    def start(self, step, str):
        if step >= len(self.progress_tasks):
            task = self.pbar.add_task(total=len(self.all), description=str)
            self.progress_tasks.append(task)

    def update(self):
        prog = np.array([x.current_step for x in self.all])

        for i, task_id in enumerate(self.progress_tasks):
            self.pbar.update(task_id, completed=sum(i < prog), total=len(prog))


def describe_coroutine(coro):
    """
    Extracts and returns the current line of code being executed in a coroutine.

    Args:
        coro: The coroutine object to inspect

    Returns:
        str: The current line of code being executed, or None if the coroutine
             has finished execution
    """

    frame = getattr(coro, "cr_frame", None)
    if frame is None:
        return

    filename = frame.f_code.co_filename
    lineno = frame.f_lineno

    # Try to get the exact source line
    line = linecache.getline(filename, lineno).strip()

    return line


async def wrap_coroutine_with_progress[T](coroutine: Coroutine[Any, Any, T], progress_tracker: InnerProgress) -> T:
    """
    Wraps a coroutine with progress tracking functionality.

    This function executes a coroutine while tracking its progress using the
    provided progress tracker. It handles the coroutine's execution state and
    ensures proper progress updates.

    Args:
        coroutine: The coroutine to wrap and execute
        progress_tracker: Progress tracking instance to use for updates

    Returns:
        The final result of the coroutine execution

    Raises:
        RuntimeError: If asyncio.wait returns no done tasks
    """
    result_to_send_into_target = None
    coro_name = getattr(coroutine, "__name__", "anonymous_coroutine")

    try:
        while True:
            yielded_awaitable = coroutine.send(result_to_send_into_target)
            progress_tracker.start(describe_coroutine(coroutine))

            done_tasks, pending_tasks = await asyncio.wait([yielded_awaitable])
            progress_tracker.done()

            if not done_tasks:
                raise RuntimeError(
                    f"asyncio.wait returned no done tasks for {coro_name} " f"while awaiting {yielded_awaitable}"
                )

            completed_task = done_tasks.pop()
            result_to_send_into_target = completed_task.result()

    except StopIteration as e:
        return e.value
    finally:
        coroutine.close()


def pbar_if_none_active() -> Progress | None:
    try:
        pbar = Progress()
        pbar.start()
    except Exception:
        pbar = None
    return pbar


async def async_map_batch[S, T](
    f: Callable[[S], Coroutine[Any, Any, T]],
    data: Iterator[S],
    batch_size: int,
    max_failure_fraction: float = 0.5,
) -> List[T]:
    """
    Process items from an iterator in batches using concurrent coroutines.

    This function processes items from an iterator in batches, executing the
    provided coroutine function concurrently for each item. It excludes failing
    samples until it can create a new batch of results of size # batch size.
    If more than max_failure_fraction % of # batch size tasks fail in the process
    of creating a new batch, the function will raise the last exception encountered.
    Results are not ordered.

    Args:
        f: Coroutine function to apply to each item
        data: Iterator of items to process
        batch_size: Number of items to process in each batch

    Returns:
        List of results from successful task executions

    Note:
        - Failed tasks are not retried
        - If more than max_failure_fraction of # batch size tasks fail, the function fails
        - Tasks are automatically cancelled if the function exits early
    """
    batch_items_from_iterator = list(itertools.islice(data, batch_size))
    num_items = len(batch_items_from_iterator)

    with Progress() as pbar:
        progress = MultiProgressTracker(pbar)

        final_results: list[Any] = [None] * num_items
        active_tasks_this_batch: Dict[asyncio.Task, int] = {}

        num_retries = 0

        for i, item_value in enumerate(batch_items_from_iterator):
            task: asyncio.Task[T] = asyncio.create_task(
                wrap_coroutine_with_progress(f(item_value), progress.new_progress())
            )
            active_tasks_this_batch[task] = i

        try:
            while active_tasks_this_batch:
                done_tasks, _ = await asyncio.wait(active_tasks_this_batch.keys(), return_when=asyncio.FIRST_COMPLETED)

                for task_item in done_tasks:
                    original_batch_slot_idx = active_tasks_this_batch.pop(task_item)

                    try:
                        result: T = await task_item
                        final_results[original_batch_slot_idx] = result
                    except Exception as ex:
                        try:
                            if num_retries > batch_size * max_failure_fraction:
                                # if more than 50% of a batch fail we'll just go on.
                                raise ex

                            logger.debug(ex)
                            retry_item_value: S = next(data)
                            new_retry_task: asyncio.Task[T] = asyncio.create_task(
                                wrap_coroutine_with_progress(f(retry_item_value), progress.new_progress())
                            )
                            active_tasks_this_batch[new_retry_task] = original_batch_slot_idx
                            num_retries += 1
                        except StopIteration:
                            ...
        finally:
            tasks_to_cancel = list(active_tasks_this_batch.keys())
            for task_to_cancel in tasks_to_cancel:
                task_to_cancel.cancel()

            if tasks_to_cancel:
                await asyncio.gather(*tasks_to_cancel, return_exceptions=True)

            pbar.refresh()

        if num_retries > 0:
            print(f"WARNING: had to retry {num_retries} times to get a batch of {batch_size}")
        ret = [res for res in final_results if res is not None]

        print(f"Final number tasks with non-None results: {len(ret)}")

        return ret


# lockstep
async def async_map_batch_lockstep[S, T](
    f: Callable[[S], Coroutine[Any, Any, T]],
    data: Iterator[S],
    batch_size: int,
) -> List[T]:
    """
    Process items from an iterator in batches using concurrent coroutines.

    This is a debugging version of async_map_batch that executes coroutines
    in lockstep, making it easier to track the execution flow and debug issues.
    Each coroutine's progress is tracked individually.

    Args:
        f: Coroutine function to apply to each item
        data: Iterator of items to process
        batch_size: Number of items to process in each batch

    Returns:
        List of results from successful task executions

    Note:
        This implementation is slower than async_map_batch but provides better
        visibility into the execution flow for debugging purposes.
    """
    batch_items_from_iterator = list(itertools.islice(data, batch_size))
    num_items = len(batch_items_from_iterator)

    with Progress() as pbar:
        progress = MultiProgressTracker(pbar)

        coroutines: List[Any] = []
        progress_trackers: List[Any] = []
        final_results: List[T | None] = [None] * num_items
        completed: List[bool] = [False] * num_items

        for item in batch_items_from_iterator:
            coro = f(item)
            coroutines.append(coro)
            progress_trackers.append(progress.new_progress())

        previous_results: Dict[int, Any] = {}

        try:
            while not all(completed):
                awaitables: Dict[int, Any] = {}

                for i, (coro, is_done) in enumerate(zip(coroutines, completed)):
                    if is_done:
                        continue

                    try:
                        result_to_send = previous_results.get(i, None)
                        awaitable = coro.send(result_to_send)
                        awaitables[i] = awaitable
                        progress_trackers[i].start(describe_coroutine(coro))
                    except StopIteration as e:
                        final_results[i] = e.value
                        completed[i] = True
                        coro.close()

                if not awaitables:
                    break

                awaitable_list = list(awaitables.items())
                awaitable_futures = []

                for idx, awaitable in awaitable_list:
                    if asyncio.iscoroutine(awaitable):
                        future = asyncio.create_task(awaitable)
                    else:
                        future = asyncio.ensure_future(awaitable)
                    awaitable_futures.append((idx, future))

                futures_only = [f for _, f in awaitable_futures]
                done_tasks, pending_tasks = await asyncio.wait(futures_only, return_when=asyncio.ALL_COMPLETED)

                results_for_next = {}
                for idx, future in awaitable_futures:
                    progress_trackers[idx].done()
                    try:
                        result = await future
                        results_for_next[idx] = result
                    except Exception as e:
                        logger.exception(f"Error in coroutine {idx}: {e}")
                        completed[idx] = True

                previous_results = results_for_next

        finally:
            for i, (coro, is_done) in enumerate(zip(coroutines, completed)):
                if not is_done:
                    coro.close()

            pbar.refresh()

        ret = [res for res in final_results if res is not None]
        print(f"Final number returned tasks: {len(ret)}")

        return ret


def log_args(func):
    """
    A Python decorator that logs the arguments of the decorated function
    to Weights & Biases (wandb) as configuration.

    Assumes that wandb has been initialized (wandb.init()) before
    the decorated function is called.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import wandb
        import json
        import inspect

        if wandb.run is None:
            print("Warning: wandb run has not been initialized. Arguments will not be logged.")
            return func(*args, **kwargs)

        # Helper to check serializability and log
        def log_if_serializable(key, value):
            try:
                # we need to log the model builder args here because they are not serializable by default
                if isinstance(value, InferenceModel) or isinstance(value, TrainingModel):
                    value = value.get_builder_args()
                else:
                    # Check if the value itself is a complex object that might not be fully serializable
                    # by trying to dump it directly.
                    json.dumps({key: value})
                wandb.config[key] = value
            except (TypeError, OverflowError) as e:
                print(
                    f"Warning: Argument '{key}' with value '{str(value)[:100]}...' "
                    f"(type: {type(value).__name__}) is not JSON serializable and will be skipped. Error: {e}"
                )

        sig = inspect.signature(func)
        bound_args = sig.bind_partial(*args, **kwargs)
        bound_args.apply_defaults()

        all_args = bound_args.arguments

        for key, value in all_args.items():
            log_if_serializable(key, value)

        return func(*args, **kwargs)

    return wrapper


async def async_map[S, T](f: Callable[[S], Coroutine[Any, Any, T]], data: Iterable[S]) -> list[T]:
    """
    Process all items in an iterable concurrently using the provided coroutine function.

    Args:
        f: Coroutine function to apply to each item
        data: Iterable of items to process

    Returns:
        List of results from all task executions
    """

    # Check if a Progress bar is already active
    pbar = pbar_if_none_active()
    try:
        if pbar is not None:
            progress = MultiProgressTracker(pbar)
            all_tasks = [
                asyncio.create_task(wrap_coroutine_with_progress(f(item), progress.new_progress())) for item in data
            ]
            results = await asyncio.gather(*all_tasks)
        else:
            all_tasks = [asyncio.create_task(f(item)) for item in data]
            results = await asyncio.gather(*all_tasks)
        return results
    finally:
        if pbar is not None:
            pbar.stop()


async def async_map_fallible[S, T](f: Callable[[S], Coroutine[Any, Any, T]], data: Iterable[S]) -> list[T]:
    """
    Process all items in an iterable concurrently using the provided coroutine function.

    Args:
        f: Coroutine function to apply to each item
        data: Iterable of items to process

    Returns:
        List of results from all task executions
    """

    async def wrap_coroutine_with_error_handling(coro: Coroutine[Any, Any, T]) -> tuple[T, bool]:
        try:
            result = await coro
            return result, True
        except Exception:
            return None, False  # type: ignore

    # Check if a Progress bar is already active
    pbar = pbar_if_none_active()
    try:
        if pbar is not None:
            progress = MultiProgressTracker(pbar)
            all_tasks = [
                asyncio.create_task(
                    wrap_coroutine_with_error_handling(wrap_coroutine_with_progress(f(item), progress.new_progress()))
                )
                for item in data
            ]
        else:
            all_tasks = [asyncio.create_task(wrap_coroutine_with_error_handling(f(item))) for item in data]
        results = await asyncio.gather(*all_tasks)
    finally:
        if pbar is not None:
            pbar.stop()

    return [result for result, success in results if success]


def get_minibatches[T](dataset: list[T], mini_batch_size: int, number_of_epochs: int) -> list[list[T]]:
    all_batches: list[list[T]] = []

    for _ in range(number_of_epochs):
        shuffled_dataset = random.sample(dataset, k=len(dataset))

        epoch_batches: list[list[T]] = []
        for i in range(0, len(shuffled_dataset), mini_batch_size):
            batch = shuffled_dataset[i : i + mini_batch_size]
            epoch_batches.append(batch)
        all_batches.extend(epoch_batches)

    return all_batches


def sample_data[T](data: list[T], epochs: float) -> list[T]:
    num_samples = len(data) * epochs
    return [data[x] for x in np.random.permutation(len(data))[: int(num_samples)]]


def weighted_mean(values: list[list[float]], weights: list[list[float]]) -> float:
    return np.average(np.concatenate(values), weights=np.concatenate(weights)).item()


def stringify_thread(thread: StringThread, sep: str = "\n\n") -> str:
    """Convert StringThread to readable text format."""
    turns = thread.get_turns()
    return sep.join([f"[{turn.role}]\n{turn.content}" for turn in turns])


SingleTurnShot = TypedDict("SingleTurnShot", {"user": dict[str, str], "assistant": dict[str, str]})


class TurnTemplates(NamedTuple):
    system: str | None
    user: str | None
    assistant: str | None
    shots: list[SingleTurnShot] | None


def turn_templates_from_dir(root_dir: str) -> TurnTemplates:
    """
    Returns system, user and assistant turn string templates from a directory, as well as a list of shot dicts.
    Expects files to be named system.md, user.md, assistant.md and shots.jsonl.
    Returns None for any turn template file that does not exist.
    """
    root_path = Path(root_dir)
    expected_files = ["system.md", "user.md", "assistant.md", "shots.jsonl"]
    missing_templates = []
    turn_templates: list[str | list[SingleTurnShot] | None] = []

    for file in expected_files:
        path = root_path / file
        if not path.exists():
            missing_templates.append(file)
            turn_templates.append(None)
        else:
            if file == "shots.jsonl":
                shots = []
                for line in path.read_text().splitlines():
                    data = json.loads(line)
                    shot = SingleTurnShot(user=data["user"], assistant=data["assistant"])
                    shots.append(shot)
                turn_templates.append(shots)
            else:
                turn_templates.append(path.read_text())

    # Ensure proper typing: first 3 are str|None, last is list[SingleTurnShot]|None
    system, user, assistant, shots = turn_templates
    return TurnTemplates(
        system=system if isinstance(system, str) else None,
        user=user if isinstance(user, str) else None,
        assistant=assistant if isinstance(assistant, str) else None,
        shots=shots if isinstance(shots, list) else None,
    )
