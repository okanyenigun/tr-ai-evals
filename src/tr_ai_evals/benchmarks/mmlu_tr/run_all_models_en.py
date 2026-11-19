"""Run every model through the original English MMLU, as a baseline for the Turkish results.

Usage: uv run src/tr_ai_evals/benchmarks/mmlu_tr/run_all_models_en.py

Same steps as run_all_models.py, with the English dataset, prompt template and subject names.
The generation settings, example questions and question ids are the same as in the Turkish run,
so the two can be compared question by question. It is safe to stop this and run it again: each
model continues where it stopped.
"""

import sys

import ollama

from tr_ai_evals.benchmarks.mmlu_tr.funcs import (
    build_manifest,
    build_prompt,
    get_model_digest,
    load_data,
    load_versioned,
    run_experiment,
    select_shots,
)

# Experiment 1 is the Turkish run; this English baseline is experiment 2.
EXPERIMENT = 2
DESCRIPTION = "Original English MMLU test split with HELM's MMLU prompts, as a baseline for MMLU-TR."

MODELS = [
    "qwen2.5:3b",
    "gemma2:2b",
    "qwen3.5:2b",
    "gemma3:4b",
    "qwen2.5:7b",
]
# Download models that are not installed. Set to False to skip them instead.
PULL_MISSING_MODELS = True
# Failed requests count as wrong and are not asked again. Set to True only when they failed
# for reasons outside the model, such as Ollama being down.
RETRY_FAILED = False

DATASET_NAME = "mmlu_en_questions"
DATASET_VERSION = "v1"
TEMPLATE_NAME = "mmlu_en_template"
TEMPLATE_VERSION = "v1"
SUBJECTS_NAME = "mmlu_en_subjects"
SUBJECTS_VERSION = "v1"
# The same generation settings as the Turkish run.
PARAMS_NAME = "mmlu_tr_params"
PARAMS_VERSION = "v1"


def prepare_model(model: str, params: dict) -> None:
    """Make sure a model is installed and can load, or raise an error saying why not."""
    client = ollama.Client()
    try:
        get_model_digest(model)
    except ValueError:
        if not PULL_MISSING_MODELS:
            raise
        print(f"Downloading {model}...", flush=True)
        client.pull(model)
    # An empty prompt only loads the model, so a broken one fails here and not on every question.
    # Loading it with the run's context length avoids a reload on the first question.
    client.generate(model=model, prompt="", options={"num_ctx": params["num_ctx"]})


def main() -> int:
    sys.stdout.reconfigure(line_buffering=True)

    data, dataset_revision = load_data(name=DATASET_NAME, version=DATASET_VERSION)
    shots = select_shots(data["dev"])
    template, template_hash = load_versioned("templates", TEMPLATE_NAME, TEMPLATE_VERSION)
    subject_names, subjects_hash = load_versioned("subjects", SUBJECTS_NAME, SUBJECTS_VERSION)
    params, params_hash = load_versioned("params", PARAMS_NAME, PARAMS_VERSION)

    def make_prompt(question: dict) -> str:
        subject = question["subject"]
        return build_prompt(template, subject_names[subject], shots[subject], question)

    summaries = {}
    problems = {}
    for position, model in enumerate(MODELS, start=1):
        print(f"\n=== Model {position} of {len(MODELS)}: {model} ===")
        try:
            prepare_model(model, params)
            manifest = build_manifest(
                experiment=EXPERIMENT,
                model=model,
                model_digest=get_model_digest(model),
                dataset=(DATASET_NAME, DATASET_VERSION, dataset_revision),
                template=(TEMPLATE_NAME, TEMPLATE_VERSION, template_hash),
                subjects=(SUBJECTS_NAME, SUBJECTS_VERSION, subjects_hash),
                params=(PARAMS_NAME, PARAMS_VERSION, params_hash),
                shots=shots,
                description=DESCRIPTION,
            )
            summaries[model] = run_experiment(
                manifest, data["test"], make_prompt, params, retry_failed=RETRY_FAILED
            )
        except Exception as error:
            problems[model] = f"{type(error).__name__}: {error}"
            print(f"Moving on from {model}: {problems[model]}")

    print(f"\n=== Experiment {EXPERIMENT} results ===")
    for model in MODELS:
        if model in summaries:
            summary = summaries[model]
            print(
                f"{model:<14} {summary['asked']} of {summary['total']} asked, "
                f"{summary['failed']} failed, {summary['invalid']} invalid, "
                f"accuracy {summary['accuracy']:.2%}"
            )
        else:
            print(f"{model:<14} NOT FINISHED: {problems[model]}")
    if problems:
        print("\nFix the problems above and run this again; finished work is kept.")
    return 1 if problems else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nStopped. Run this again to continue where each model stopped.")
        sys.exit(130)
