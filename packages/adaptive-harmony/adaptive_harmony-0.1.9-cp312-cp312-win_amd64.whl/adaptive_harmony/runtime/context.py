import inspect
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from adaptive_harmony import HarmonyClient, get_client, JobNotifier, HarmonyJobNotifier
from adaptive_harmony.file_storage import FileStorage, FileStorageConfig
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.table import Table as RichTable
from typing import Self

from adaptive_harmony import EvalSample
from adaptive_harmony.internal import _extract_model_key, _save_detailed_eval_table


class RecipeConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ADAPTIVE_", cli_parse_args=True, cli_kebab_case=True)

    harmony_url: str = Field(description="url of harmony service")
    user_input_file: str | None = None
    job_id: str = "test"
    use_case: str | None = None
    api_key: str | None = None
    compute_pool: str | None = None
    storage_url: str | None = None
    num_gpus: int = 0


class RecipeContext:
    client: HarmonyClient
    job: JobNotifier
    file_storage: FileStorage
    config: RecipeConfig
    # todo: pass world size
    world_size: int = 1

    def __init__(self, client: HarmonyClient, config: RecipeConfig):
        self.client = client
        self.config = config
        self.job = HarmonyJobNotifier(client, config.job_id)
        if config.storage_url:
            # todo: handle s3 ?
            self.file_storage = FileStorage.new(FileStorageConfig.from_url(config.storage_url))
        else:
            self.file_storage = FileStorage.new(FileStorageConfig.from_url("file:///tmp/recipe_storage"))

    @classmethod
    async def load(cls) -> Self:
        config = RecipeConfig()  # type: ignore
        return await cls.from_config(config)

    @classmethod
    async def from_config(cls, config: RecipeConfig) -> Self:
        client = await get_client(
            config.harmony_url,
            num_gpus=config.num_gpus,
            api_key=config.api_key,
            use_case=config.use_case,
            compute_pool=config.compute_pool,
        )
        return cls(client, config)

    @staticmethod
    def log_eval_result(eval_samples: list[EvalSample]) -> None:
        # Convert to DataFrame for easy aggregation
        data = []
        for eval_sample in eval_samples:
            for grade in eval_sample.grades:
                data.append(
                    {
                        "model": _extract_model_key(eval_sample.interaction.source),
                        "grader": grade.grader_key,
                        "score": grade.value,
                    }
                )
        df = pd.DataFrame(data)

        # Create pivot table with models as rows and graders as columns
        if not df.empty:
            pivot_df = df.pivot_table(index="model", columns="grader", values="score", aggfunc="mean")

            # Create Rich table from pivot
            console = Console()
            table = RichTable(title="GRADER EVALUATION RESULTS")
            table.add_column("Model", style="cyan", no_wrap=True)
            # One column per grader
            for grader_name in pivot_df.columns:
                table.add_column(grader_name, justify="center")

            # Find the maximum score for each grader (excluding NaN values)
            max_scores = {}
            for grader_name in pivot_df.columns:
                valid_scores = pivot_df[grader_name].dropna()
                if len(valid_scores) > 0:
                    max_scores[grader_name] = valid_scores.max()

            # One row per model
            for model_name in pivot_df.index:
                row = [model_name]
                for grader_name in pivot_df.columns:
                    score = pivot_df.loc[model_name, grader_name]
                    # Avg will be nan if grader failed on all samples
                    if pd.isna(score):
                        row.append("All failed")
                    else:
                        score_str = f"{score:.3f}"
                        # Highlight the highest score in green
                        if grader_name in max_scores and abs(score - max_scores[grader_name]) < 1e-9:
                            row.append(f"[green]{score_str}[/green]")
                        else:
                            row.append(score_str)
                table.add_row(*row)

            console.print(table)

            # Get the directory of the original caller (skip this method's frame)
            caller_frame = inspect.currentframe()
            original_caller_dir = None
            if caller_frame is not None and caller_frame.f_back is not None:
                original_caller_file = caller_frame.f_back.f_globals["__file__"]
                original_caller_dir = str(Path(original_caller_file).parent)

            # Save compact JSON of grader results
            original_caller_dir = original_caller_dir or Path.cwd()
            results_json = {}
            for model_name in pivot_df.index:
                results_json[model_name] = {}
                for grader_name in pivot_df.columns:
                    score = pivot_df.loc[model_name, grader_name]
                    if pd.isna(score):
                        results_json[model_name][grader_name] = None
                    else:
                        # Convert pandas scalar to native Python type
                        score_val = score.item() if hasattr(score, "item") else float(score)  # type: ignore
                        results_json[model_name][grader_name] = round(score_val, 3)  # type:ignore

            timestamp = datetime.now().replace(microsecond=0).isoformat()
            eval_dir = Path(original_caller_dir) / "adaptive_eval_samples" / timestamp
            eval_dir.mkdir(parents=True, exist_ok=True)

            results_path = eval_dir / "aggregate_scores.json"
            with open(results_path, "w") as f:
                json.dump(results_json, f, indent=2)
            print(f"\n📁 Aggregate results saved to: {results_path}")

            # Save detailed evaluation samples as html
            _save_detailed_eval_table(eval_samples, output_dir=str(eval_dir))
        else:
            print("No evaluation data to display")
