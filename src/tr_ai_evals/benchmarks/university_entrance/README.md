# Turkish University Entrance Exam Benchmark

Runs models served by Ollama on 4,858 multiple-choice questions from Turkish university entrance exams, and saves every answer. Results are in the [benchmark report](../../../../docs/reports/university_entrance_report.md).

## Folder contents

| Path | Purpose |
|---|---|
| `run_all_models.py` | Runs every model in `MODELS`; safe to stop and restart |
| `funcs.py` | Loads versioned components, runs questions, saves answers and manifests |
| `human_queries.py` | Question-format builders, by version |
| `schemas.py` | Answer schemas, by version |
| `prompts/` | System prompts: `<name>_<version>.txt` |
| `params/` | Generation settings: `<name>_<version>.json` |
| `data_versions/` | Dataset versions, each pinned to a Hub revision: `<name>_<version>.json` |
| `example.ipynb` | Step-by-step run of a single model |
| `experiments/` | Run outputs; ignored by git |

## Requirements

- Ollama running locally. Missing models are downloaded when `PULL_MISSING_MODELS = True`.
- Access to the dataset [`yeniguno/turkish-university-entrance-exam-questions`](https://huggingface.co/datasets/yeniguno/turkish-university-entrance-exam-questions). Log in to Hugging Face if it requires it.

## Running

From the repository root:

```
uv run src/tr_ai_evals/benchmarks/university_entrance/run_all_models.py
```

- **Resuming:** stop with Ctrl+C and run again to continue where each model stopped.
- **Exit code:** 1 if any model didn't finish; the reason is printed at the end.

## Configuration

Set at the top of `run_all_models.py`:

| Constant | Purpose |
|---|---|
| `EXPERIMENT` | Experiment number, used for the output folder |
| `DESCRIPTION` | Free text saved in each manifest |
| `MODELS` | Ollama model tags to run |
| `PULL_MISSING_MODELS` | Download models that aren't installed |
| `RETRY_FAILED` | Ask failed questions again; keep `False` unless they failed for reasons outside the model |
| `DATASET_NAME`, `DATASET_VERSION` | Dataset version in `data_versions/` |
| `PROMPT_NAME`, `PROMPT_VERSION` | System prompt in `prompts/` |
| `HUMAN_QUERY_NAME`, `HUMAN_QUERY_VERSION` | Question format in `human_queries.py` |
| `MODEL_PARAMS_NAME`, `MODEL_PARAMS_VERSION` | Generation settings in `params/` |
| `SCHEMA_NAME`, `SCHEMA_VERSION` | Answer schema in `schemas.py` |

## Versioned components

Each component is selected by name and version, and its hash is saved in the manifest. Never edit a published version; add a new one.

| Component | Location | Identified by |
|---|---|---|
| Dataset | `data_versions/` | Hub revision |
| System prompt | `prompts/` | Hash of the text |
| Question format | `HUMAN_QUERIES` in `human_queries.py` | Hash of the prompts rendered for `REFERENCE_ROWS` |
| Generation settings | `params/` | Hash of the JSON |
| Answer schema | `SCHEMAS` in `schemas.py` | Hash of the JSON schema |

To add a version:

- **File-based components:** add a new file, e.g. `prompts/tr_uni_exam_system_v2.txt`.
- **Code-based components:** add a new entry to `HUMAN_QUERIES` or `SCHEMAS`.

Then point the constants in `run_all_models.py` to it. A refactor that renders the same prompts or schema keeps the same hash.

## Run outputs

Each run is saved to `experiments/experiment_<number>/<run id>/`.

The run ID is the model name plus a hash of the experiment, model, model digest, dataset, prompt, question format, generation settings and schema. The same settings continue the same run, and any change starts a new one. Code changes don't change the run ID.

| File | Content |
|---|---|
| `manifest.json` | Run settings, model digest, component versions and hashes, git commit, start time |
| `answers.jsonl` | One line per attempt: `question_id`, `llm_answer` (`{id, code}` or `null`), `correct_answer`, `error`, `seconds` |

The latest line for each question is the one that counts. To load a whole experiment, use `funcs.load_experiment(<number>)`, which returns `{run id: (manifest, latest record per question)}`.

## Failure handling

- **Failed answers:** a failed answer is saved with its error, counts as wrong and isn't asked again, unless `RETRY_FAILED = True`.
- **Safety stops:** a model is stopped after 50 failures in a row, or if its accuracy is below 10% after 100 questions. The script then moves on to the next model, and saved answers are kept.
