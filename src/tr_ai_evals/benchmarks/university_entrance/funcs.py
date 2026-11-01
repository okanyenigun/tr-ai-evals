import ollama
import contextlib
import hashlib
import json
import os
import re
import subprocess
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from pydantic import BaseModel
from datasets import DatasetDict, load_dataset
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from human_queries import HUMAN_QUERIES, REFERENCE_ROWS
from schemas import SCHEMAS

DATASET_NAME = "yeniguno/turkish-university-entrance-exam-questions"
PROMPTS_DIR = Path(__file__).parent / "prompts"
PARAMS_DIR = Path(__file__).parent / "params"
DATA_VERSIONS_DIR = Path(__file__).parent / "data_versions"
EXPERIMENTS_DIR = Path(__file__).parent / "experiments"
# The longest run of failures in a real experiment so far is 47. More means something is broken.
MAX_CONSECUTIVE_FAILURES = 50
# Guessing scores 20%, so scoring under this many questions in means something is broken.
MIN_ACCURACY = 0.1
MIN_ACCURACY_AFTER = 100
# The manifest fields that define a run. The same values always give the same run id.
RUN_ID_FIELDS = (
    "experiment",
    "model",
    "model_digest",
    "dataset",
    "prompt",
    "human_query",
    "params",
    "schema",
)


def load_hub_dataset(revision: str) -> DatasetDict:
    """Download the dataset from the Hub at a specific revision."""
    # The repo root has a local yeniguno/<dataset> folder that would shadow the Hub repo.
    with contextlib.chdir(Path(__file__).parent):
        return load_dataset(DATASET_NAME, revision=revision)


def load_train_data(name: str, version: str) -> tuple[list[dict], str]:
    """Load data_versions/<name>_<version>.json; return ("train" rows as dicts, Hub revision).

    The revision is an immutable Hub commit, so it identifies the data the way a hash would.
    Log the name, version and revision with every eval result.
    """
    spec = json.loads(
        (DATA_VERSIONS_DIR / f"{name}_{version}.json").read_text(encoding="utf-8")
    )
    return load_hub_dataset(revision=spec["revision"])["train"].to_list(), spec[
        "revision"
    ]


def load_prompt(name: str, version: str) -> tuple[str, str]:
    """Load prompts/<name>_<version>.txt; return (text, 8-char sha256 hash).

    Log the name, version and hash with every eval result.
    """
    text = (PROMPTS_DIR / f"{name}_{version}.txt").read_text(encoding="utf-8").strip()
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


def load_human_query(name: str, version: str) -> tuple[Callable[[dict], str], str]:
    """Look up a prompt builder in human_queries.HUMAN_QUERIES; return (function, 8-char hash).

    The hash covers the prompts it renders for human_queries.REFERENCE_ROWS, not the
    Python source, so a refactor keeps the hash and any change to a prompt does not.
    """
    build = HUMAN_QUERIES[(name, version)]
    rendered = json.dumps([build(row) for row in REFERENCE_ROWS], ensure_ascii=False)
    return build, hashlib.sha256(rendered.encode("utf-8")).hexdigest()[:8]


def load_params(name: str, version: str) -> tuple[dict, str]:
    """Load params/<name>_<version>.json; return (params dict, 8-char sha256 hash).

    Keep endpoints and credentials out of these files; they are not generation settings.
    """
    params = json.loads(
        (PARAMS_DIR / f"{name}_{version}.json").read_text(encoding="utf-8")
    )
    canonical = json.dumps(params, sort_keys=True)
    return params, hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:8]


def load_schema(name: str, version: str) -> tuple[type[BaseModel], str]:
    """Look up a structured-output model in schemas.SCHEMAS; return (class, 8-char hash).

    The hash covers the JSON schema the LLM sees (field names, types, descriptions),
    not the Python source.
    """
    cls = SCHEMAS[(name, version)]
    canonical = json.dumps(cls.model_json_schema(), sort_keys=True, ensure_ascii=False)
    return cls, hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:8]


def ask_to_llm(
    llm: Runnable, system_prompt: str, human_query: str, image: str | None = None
) -> BaseModel:
    """Send one question to llm, attaching its base64 PNG image if it has one."""
    content = human_query
    if image:
        content = [
            {"type": "text", "text": human_query},
            {"type": "image", "base64": image, "mime_type": "image/png"},
        ]
    return llm.invoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=content)]
    )


def read_answers(path: Path) -> dict[int, dict]:
    """Return the latest saved record for each question id in an answers.jsonl file."""
    if not path.exists():
        return {}
    data = path.read_bytes()
    complete = data.rfind(b"\n") + 1
    if complete < len(data):
        # A crash can leave a half-written last line. Drop it so the next append starts clean.
        os.truncate(path, complete)
    lines = data[:complete].decode("utf-8").split("\n")[:-1]
    return {record["question_id"]: record for record in map(json.loads, lines)}


def generate_run_id(manifest: dict) -> str:
    """Return a run id such as gemma3-4b_1a2b3c4d: the model name plus a hash of the run's settings."""
    settings = {field: manifest[field] for field in RUN_ID_FIELDS}
    canonical = json.dumps(settings, sort_keys=True, ensure_ascii=False)
    model = re.sub(r"[^A-Za-z0-9.]+", "-", manifest["model"])
    return f"{model}_{hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:8]}"


def summarize_answers(records: dict[int, dict], total: int) -> dict:
    """Count an experiment's results. Failed questions count as wrong in the accuracy."""
    answered = [
        record for record in records.values() if record["llm_answer"] is not None
    ]
    correct = sum(
        record["llm_answer"]["code"] == record["correct_answer"] for record in answered
    )
    return {
        "total": total,
        "answered": len(answered),
        "failed": len(records) - len(answered),
        "not_asked": total - len(records),
        "correct": correct,
        "accuracy": correct / len(records) if records else 0.0,
    }


def run_experiment(
    manifest: dict,
    llm: Runnable,
    system_prompt: str,
    build_human_query: Callable[[dict], str],
    questions: list[dict],
) -> dict:
    """Ask every question, saving each answer as it arrives; a re-run continues where this one stopped.

    Results go to experiments/experiment_<number>/<run id>/: manifest.json and answers.jsonl,
    with one line per attempt. The same settings give the same run id, so they continue the same
    run; different settings start a new one. Questions not asked yet come first, then earlier
    failures are retried.
    """
    run_id = generate_run_id(manifest)
    folder = EXPERIMENTS_DIR / f"experiment_{manifest['experiment']}" / run_id
    folder.mkdir(parents=True, exist_ok=True)
    manifest_path = folder / "manifest.json"
    if not manifest_path.exists():
        temporary = manifest_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps({**manifest, "run_id": run_id}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(manifest_path)
    answers_path = folder / "answers.jsonl"
    records = read_answers(answers_path)

    not_asked = [question for question in questions if question["id"] not in records]
    to_retry = [
        question
        for question in questions
        if question["id"] in records and records[question["id"]]["llm_answer"] is None
    ]
    print(
        f"Experiment {manifest['experiment']}, run {run_id}: {len(questions) - len(not_asked) - len(to_retry)} done, "
        f"{len(not_asked)} not asked, {len(to_retry)} failed before and will be retried."
    )

    consecutive_failures = 0
    with open(answers_path, "a", encoding="utf-8") as answers_file:
        for position, question in enumerate(not_asked + to_retry):
            human_query = build_human_query(question)
            started = time.perf_counter()
            try:
                answer = ask_to_llm(
                    llm, system_prompt, human_query, question["image"]
                ).model_dump(mode="json")
                error = None
            except Exception as exception:
                answer = None
                error = f"{type(exception).__name__}: {exception}"[:500]
            record = {
                "question_id": question["id"],
                "llm_answer": answer,
                "correct_answer": question["answer"],
                "error": error,
                "seconds": round(time.perf_counter() - started, 3),
            }
            answers_file.write(json.dumps(record, ensure_ascii=False) + "\n")
            answers_file.flush()
            records[question["id"]] = record

            summary = summarize_answers(records, len(questions))
            if (position + 1) % 10 == 0:
                print(
                    f"{len(records)} / {len(questions)} questions, accuracy {summary['accuracy']:.2%}"
                )

            consecutive_failures = consecutive_failures + 1 if error else 0
            if position < len(not_asked):
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    raise RuntimeError(
                        f"Stopped after {consecutive_failures} failures in a row. Last error: {error}. "
                        "Fix the problem and run again; failed questions will be retried."
                    )
                if (
                    len(records) == MIN_ACCURACY_AFTER
                    and summary["accuracy"] < MIN_ACCURACY
                ):
                    raise RuntimeError(
                        f"Accuracy is {summary['accuracy']:.2%} after {len(records)} questions, which suggests "
                        "something is broken. Saved answers are kept; running again continues past this check."
                    )

    summary = {"run_id": run_id, **summarize_answers(records, len(questions))}
    print(f"Finished: {summary}")
    return summary


def load_experiment(experiment: int) -> dict[str, tuple[dict, list[dict]]]:
    """Return {run id: (manifest, latest record for each question)} for every run in an experiment."""
    runs = {}
    for manifest_path in sorted(
        (EXPERIMENTS_DIR / f"experiment_{experiment}").glob("*/manifest.json")
    ):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        runs[manifest["run_id"]] = (
            manifest,
            list(read_answers(manifest_path.parent / "answers.jsonl").values()),
        )
    return runs


def get_model_digest(model: str, host: str | None = None) -> str:
    """Return the digest of an installed Ollama model, which identifies its exact weights."""
    name = model if ":" in model else f"{model}:latest"
    for installed in ollama.Client(host=host).list().models:
        if installed.model == name:
            return installed.digest
    raise ValueError(f"Model {name} is not installed in Ollama.")


def build_manifest(
    model: str,
    model_digest: str | None,
    dataset: tuple[str, str, str],
    prompt: tuple[str, str, str],
    human_query: tuple[str, str, str],
    params: tuple[str, str, str],
    schema: tuple[str, str, str],
    experiment: int,
    **extra,
) -> dict:
    """Build a run manifest to save next to eval outputs.

    model_digest: from get_model_digest, or None for a model that has no digest, such as a hosted one.
    dataset: (name, version, revision). prompt, human_query, params, schema: (name, version, hash).
    Record how the schema is enforced via extra, e.g. output_mode="native_structured".
    Pass anything else worth recording as keyword args, e.g. parser_version, ignored_params.
    """
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit = None
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "experiment": experiment,
        "model": model,
        "model_digest": model_digest,
        "dataset": dict(zip(("name", "version", "revision"), dataset)),
        "prompt": dict(zip(("name", "version", "hash"), prompt)),
        "human_query": dict(zip(("name", "version", "hash"), human_query)),
        "params": dict(zip(("name", "version", "hash"), params)),
        "schema": dict(zip(("name", "version", "hash"), schema)),
        "git_commit": commit,
        **extra,
    }
