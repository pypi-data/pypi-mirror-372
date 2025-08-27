import numpy as np
from loguru import logger as loguru
from typing import Callable, Awaitable, Any
from adaptive_harmony import StringThread, TrainingModel, TokenizedThread
from adaptive_harmony.core.utils import async_map_fallible


async def generate_and_score(
    model: TrainingModel, scoring_fn: Callable[[StringThread], Awaitable[float]], prompt: StringThread
) -> tuple[TokenizedThread, StringThread, float]:
    """Generate tokens from a prompt and score the resulting string sample."""
    sample = await model.generate_tokens(prompt)
    string_sample = await model.detokenize_thread(sample)
    score = await scoring_fn(string_sample)
    return sample, string_sample, score


async def run_validation(
    validation_samples: list[StringThread],
    model: TrainingModel,
    scoring_fn: Callable[[StringThread], Awaitable[float]],
) -> dict[str, Any]:
    """
    Run validation on a set of samples and return validation metrics to log.

    Args:
        validation_samples: List of prompts to validate on
        model: The model to use for generation
        scoring_fn: Function to score generated samples

    Returns:
        Dict containing validation metrics
    """
    loguru.info("Entering validation")
    validation_results = await async_map_fallible(
        lambda prompt: generate_and_score(model, scoring_fn, prompt), validation_samples
    )
    scores = [score for _, _, score in validation_results]
    gen_lengths = [sample.len_last_turn() for sample, _, _ in validation_results]

    validation_logs = dict(
        **{
            f"validation/{key}": value
            for key, value in dict(
                score_mean=np.mean(scores).item(),
                generation_length_mean=np.mean(gen_lengths).item(),
                generation_length_std=np.std(gen_lengths).item(),
                num_samples=len(validation_results),
            ).items()
        }
    )

    loguru.info(f"Validation complete\nMean score: {validation_logs['validation/score_mean']:.4f}")
    return validation_logs
