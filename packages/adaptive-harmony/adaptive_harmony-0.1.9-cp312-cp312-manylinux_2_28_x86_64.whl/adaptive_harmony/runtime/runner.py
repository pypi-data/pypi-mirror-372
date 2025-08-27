import sys
import os
import asyncio
import importlib
import inspect
import traceback
from typing import Any
from adaptive_harmony.runtime.data import InputConfig
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from adaptive_harmony.runtime.context import RecipeConfig, RecipeContext


class RunnerArgs(RecipeConfig, BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ADAPTIVE_", cli_parse_args=True, cli_kebab_case=True)

    recipe_file: str = Field(description="the python recipe file to execute")


def main():
    runner_args = RunnerArgs()  # type: ignore
    context = asyncio.run(RecipeContext.from_config(runner_args))
    logger.trace("Loaded config: {}", context.config)
    try:
        _load_and_run_recipe(context, runner_args.recipe_file)
    except Exception as e:
        stack_trace = traceback.format_exc()
        logger.exception(f"Error while running recipe file {runner_args.recipe_file}", exception=e)
        context.job.report_error(stack_trace)
        sys.exit(1)


def _load_and_run_recipe(context: RecipeContext, recipe_file: str):
    recipe_abs_path = os.path.abspath(recipe_file)
    if not os.path.isfile(recipe_abs_path):
        raise FileNotFoundError(f"Recipe file '{recipe_abs_path}' does not exist.")
    recipe_filename = os.path.basename(recipe_abs_path)
    recipe_name = os.path.splitext(recipe_filename)[0]
    logger.trace(f"Recipe file found: {recipe_filename}")

    # import file as python module
    sys.path.insert(0, os.path.dirname(recipe_abs_path))
    recipe_module = importlib.import_module(recipe_name)

    # get recipe_main function
    functions = inspect.getmembers(recipe_module, inspect.isfunction)
    recipe_main_functions = [(name, func) for name, func in functions if getattr(func, "is_recipe_main", False)]

    if len(recipe_main_functions) == 0:
        logger.warning("No function annotated with @recipe_main")
        return

    if len(recipe_main_functions) != 1:
        names = [name for (name, _) in recipe_main_functions]
        raise ValueError(f"You must have only one function annotated with @recipe_main. Found {names}")

    (func_name, func) = recipe_main_functions[0]
    logger.trace("Getting recipe function parameters")
    args = _get_params(func, context)

    logger.info(f"Executing recipe function {func_name}")
    if inspect.iscoroutinefunction(func):
        asyncio.run(func(*args))
    else:
        func(*args)
    logger.info(f"Recipe {func_name} completed successfully.")


def _get_params(func, context: RecipeContext) -> list[Any]:
    args: list[Any] = []
    sig = inspect.signature(func)
    assert len(sig.parameters.items()) <= 2, "Support only functions with 2 parameters or less"

    for _, param in sig.parameters.items():
        # Ensure param.annotation is a type before using issubclass
        if isinstance(param.annotation, type):
            if issubclass(param.annotation, RecipeContext):
                args.append(context)
            elif issubclass(param.annotation, InputConfig):
                if context.config.user_input_file:
                    user_input = param.annotation.load_from_file(context.config.user_input_file)
                else:
                    user_input = param.annotation()
                logger.trace("Loaded user input: {}", user_input)
                args.append(user_input)
        else:
            raise TypeError(f"Parameter '{param.name}' must have a type annotation.")

    return args


if __name__ == "__main__":
    main()
