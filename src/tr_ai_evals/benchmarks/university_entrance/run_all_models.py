"""Run every model through the benchmark, following the same steps as flow.ipynb.

Usage: python oss/run_all_models.py

It is safe to stop this and run it again: each model continues where it stopped.
"""

import sys
import ollama
from langchain_ollama import ChatOllama
from funcs import (
    build_manifest,
    get_model_digest,
    load_human_query,
    load_params,
    load_prompt,
    load_schema,
    load_train_data,
    run_experiment,
)

EXPERIMENT = 1
DESCRIPTION = "Benchmark of 10 models on the cleaned dataset with versioned prompts."

MODELS = [
    "gemma3:27b",
    "gemma4:31b",
    "qwen3.8:27b",
    "ministral-3:14b",
    "gemma4:e4b",
    "mistral-small3.2:latest",
    "gemma3:4b",
    "ornith-1.5:35b",
    "muse-glimmer:30b",
    "llama3.2-vision",
]
# Download models that are not installed. Set to False to skip them instead.
PULL_MISSING_MODELS = True

DATASET_NAME = "tr_uni_exam_questions"
DATASET_VERSION = "v1"
PROMPT_NAME = "tr_uni_exam_system"
PROMPT_VERSION = "v1"
HUMAN_QUERY_NAME = "tr_uni_exam_human_query"
HUMAN_QUERY_VERSION = "v1"
MODEL_PARAMS_NAME = "tr_uni_exam_params"
MODEL_PARAMS_VERSION = "v1"
SCHEMA_NAME = "tr_uni_exam_answer"
SCHEMA_VERSION = "v1"


def prepare_model(model: str) -> None:
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
    client.generate(model=model, prompt="")


def main() -> int:
    sys.stdout.reconfigure(line_buffering=True)

    data, dataset_revision = load_train_data(name=DATASET_NAME, version=DATASET_VERSION)
    system_prompt, prompt_hash = load_prompt(name=PROMPT_NAME, version=PROMPT_VERSION)
    build_human_query, human_query_hash = load_human_query(
        name=HUMAN_QUERY_NAME, version=HUMAN_QUERY_VERSION
    )
    model_params, model_params_hash = load_params(
        name=MODEL_PARAMS_NAME, version=MODEL_PARAMS_VERSION
    )
    answer_schema, schema_hash = load_schema(name=SCHEMA_NAME, version=SCHEMA_VERSION)

    summaries = {}
    problems = {}
    for position, model in enumerate(MODELS, start=1):
        print(f"\n=== Model {position} of {len(MODELS)}: {model} ===")
        try:
            prepare_model(model)
            manifest = build_manifest(
                model=model,
                model_digest=get_model_digest(model),
                dataset=(DATASET_NAME, DATASET_VERSION, dataset_revision),
                prompt=(PROMPT_NAME, PROMPT_VERSION, prompt_hash),
                human_query=(HUMAN_QUERY_NAME, HUMAN_QUERY_VERSION, human_query_hash),
                params=(MODEL_PARAMS_NAME, MODEL_PARAMS_VERSION, model_params_hash),
                schema=(SCHEMA_NAME, SCHEMA_VERSION, schema_hash),
                experiment=EXPERIMENT,
                description=DESCRIPTION,
            )
            llm = ChatOllama(model=model, **model_params).with_structured_output(
                answer_schema
            )
            summaries[model] = run_experiment(
                manifest, llm, system_prompt, build_human_query, data
            )
        except Exception as error:
            problems[model] = f"{type(error).__name__}: {error}"
            print(f"Moving on from {model}: {problems[model]}")

    print(f"\n=== Experiment {EXPERIMENT} results ===")
    for model in MODELS:
        if model in summaries:
            summary = summaries[model]
            print(
                f"{model:<26} {summary['answered']} of {summary['total']} answered, "
                f"{summary['failed']} failed, accuracy {summary['accuracy']:.2%}"
            )
        else:
            print(f"{model:<26} NOT FINISHED: {problems[model]}")
    if problems:
        print("\nFix the problems above and run this again; finished work is kept.")
    return 1 if problems else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nStopped. Run this again to continue where each model stopped.")
        sys.exit(130)
