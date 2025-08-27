import json
from pathlib import Path

from adaptive_harmony import StringThread, EvalSample
from adaptive_harmony.core.utils import stringify_thread
from adaptive_harmony.logging_table import Table


def _extract_model_key(model_path: str | None = None) -> str:
    model_path = model_path or ""
    if model_path.startswith("model_registry://"):
        return model_path[len("model_registry://") :]
    return model_path


def _save_detailed_eval_table(eval_samples: list[EvalSample], output_dir: str | None = None) -> None:
    """
    Method subject to change, only for internal library use.
    Do not use on its own, use RecipeContext.log_eval_result instead.
    """
    default_output_file: str = "evaluation_samples.html"
    if not eval_samples:
        print("No evaluation samples to save")
        return

    # Force provided path into dir
    if output_dir is not None:
        output_path = Path(output_dir)
        if output_path.is_file() or output_path.suffix:
            eval_dir = output_path.parent
        else:
            eval_dir = output_path
    else:
        eval_dir = Path.cwd()

    # Create the directory structure
    eval_dir.mkdir(parents=True, exist_ok=True)
    html_path = eval_dir / Path(default_output_file).name

    # Collect all unique grader names to determine column structure
    all_grader_names = set()
    for sample in eval_samples:
        for grade in sample.grades:
            all_grader_names.add(grade.grader_key)

    all_grader_names = sorted(all_grader_names)

    # Create Table
    headers = ["Prompt", "Model", "Completion"]
    for grader_name in all_grader_names:
        headers.extend([f"{grader_name}_score", f"{grader_name}_reason"])

    table = Table(headers)

    # Group samples by prompt (stringified thread)
    prompt_groups = {}
    for sample in eval_samples:
        # Extract just the prompt part (everything except the last assistant turn) for grouping
        turns = sample.interaction.thread.get_turns()
        # Find prompt turns (everything except the last assistant turn)
        prompt_turns: list[tuple[str, str]] = []
        completion = ""
        # Get all turns except extract the completion separately
        for i, (role, content) in enumerate(turns):
            if role.lower() == "assistant" and i == len(turns) - 1:
                completion = content
            else:
                prompt_turns.append((role, content))

        # Create prompt string for grouping
        prompt_str = stringify_thread(StringThread(prompt_turns))
        if prompt_str not in prompt_groups:
            prompt_groups[prompt_str] = []

        prompt_groups[prompt_str].append(
            {
                "model": _extract_model_key(sample.interaction.source or "Unknown"),
                "completion": completion,
                "grades": sample.grades,
            }
        )

    # Create table rows
    for prompt_str, models_data in prompt_groups.items():
        for i, model_data in enumerate(models_data):
            row = [
                prompt_str if i == 0 else "",  # Only show prompt for first model in group
                model_data["model"],
                model_data["completion"],
            ]

            # Add grader score and reasoning columns
            grade_dict = {grade.grader_key: grade for grade in model_data["grades"]}

            for grader_name in all_grader_names:
                if grader_name in grade_dict:
                    grade = grade_dict[grader_name]
                    row.extend([grade.value, grade.reasoning or ""])
                else:
                    row.extend(["N/A", "No evaluation"])

            table.add_row(row)

    # Save HTML table
    with open(html_path, "w") as f:
        f.write(table.to_html_table())

    # Save summary metadata as JSON
    metadata = {
        "total_samples": len(eval_samples),
        "unique_prompts": len(prompt_groups),
        "models": sorted(
            set(model_data["model"] for models_data in prompt_groups.values() for model_data in models_data)
        ),
        "graders": all_grader_names,
    }
    metadata_path = eval_dir / "metadata.json"

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"📁 Detailed evaluation samples saved to: {html_path}")
