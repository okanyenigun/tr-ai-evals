"""Building blocks for the MMLU-TR benchmark.

Prompts follow Stanford HELM's MMLU leaderboard, translated into Turkish: a header naming the subject,
5 example questions from the dev split, then the test question. The model generates one token as
plain text, and the answer is correct when it's the right letter.

The same code runs the original English MMLU as a baseline, with HELM's English prompts. Its questions
get the same ids as their Turkish translations, so the two can be compared question by question.
"""

import hashlib
import json
import os
import random
import re
import subprocess
import time
from collections import defaultdict
from datetime import UTC, datetime
from itertools import cycle
from pathlib import Path

import ollama
from datasets import load_dataset

HERE = Path(__file__).parent
EXPERIMENTS_DIR = HERE / "experiments"
LETTERS = "ABCD"
METHOD = "helm_plain_text"
# The manifest fields that define a run. The same values always give the same run id.
RUN_ID_FIELDS = (
    "experiment",
    "method",
    "model",
    "model_digest",
    "dataset",
    "template",
    "subjects",
    "params",
    "shots",
)
# More failed requests in a row than this means something is broken.
MAX_CONSECUTIVE_FAILURES = 50
# Guessing scores 25%, so scoring under this many questions in means something is broken.
MIN_ACCURACY = 0.1
MIN_ACCURACY_AFTER = 100
# Ollama cuts a prompt that doesn't fit in num_ctx without an error; one this close was probably cut.
CONTEXT_MARGIN = 64
REQUEST_TIMEOUT = 300
PROGRESS_EVERY = 500


def short_hash(value) -> str:
    """Return an 8-character sha256 of value's canonical JSON."""
    canonical = json.dumps(value, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:8]


def from_cais_mmlu(rows: list[dict], split: str) -> list[dict]:
    """Give original MMLU rows the same fields as mmlu-tr.

    Ids are <subject>_<split>_<number> in file order, as in mmlu-tr, whose rows are in the same order.
    Answers become letters, and the English text is also stored as question_en and choices_en.
    """
    counts = defaultdict(int)
    converted = []
    for row in rows:
        counts[row["subject"]] += 1
        converted.append({
            "id": f"{row['subject']}_{split}_{counts[row['subject']]:04d}",
            "subject": row["subject"],
            "question": row["question"],
            "choices": row["choices"],
            "answer": LETTERS[row["answer"]],
            "question_en": row["question"],
            "choices_en": row["choices"],
        })
    return converted


def load_data(name: str, version: str) -> tuple[dict[str, list[dict]], str]:
    """Download the dataset pinned in data_versions/<name>_<version>.json; return ({split: rows}, revision).

    The revision is an immutable Hub commit, so it identifies the data the way a hash would.
    Each split's row count is checked against the version file.
    """
    spec = json.loads(
        (HERE / "data_versions" / f"{name}_{version}.json").read_text(encoding="utf-8")
    )
    dataset = load_dataset(spec["repo"], spec.get("config"), revision=spec["revision"])
    data = {split: dataset[split].to_list() for split in spec["num_rows"]}
    if spec.get("source_format") == "cais_mmlu":
        data = {split: from_cais_mmlu(rows, split) for split, rows in data.items()}
    for split, expected in spec["num_rows"].items():
        if len(data[split]) != expected:
            raise ValueError(f"The {split} split has {len(data[split])} rows, expected {expected}.")
    return data, spec["revision"]


def load_versioned(folder: str, name: str, version: str) -> tuple[dict, str]:
    """Load <folder>/<name>_<version>.json; return (content, 8-character hash).

    Used for templates/, subjects/ and params/. Never edit a published version; add a new one.
    """
    content = json.loads((HERE / folder / f"{name}_{version}.json").read_text(encoding="utf-8"))
    return content, short_hash(content)


def select_shots(dev: list[dict], k: int = 5, seed: int = 0) -> dict[str, list[dict]]:
    """Choose and order each subject's example questions exactly as HELM does; return {subject: rows}.

    This is HELM's sample_examples, run per subject with the same seed. HELM labels each example
    by the English text of its correct answer, so the English fields decide the order.
    """
    by_subject = defaultdict(list)
    for row in dev:
        by_subject[row["subject"]].append(row)

    shots = {}
    for subject, rows in sorted(by_subject.items()):
        rng = random.Random(seed)
        by_label = defaultdict(list)
        for row in rows:
            by_label[row["choices_en"][LETTERS.index(row["answer"])]].append(row)
        labels_by_count = defaultdict(list)
        for label, items in sorted(by_label.items()):
            labels_by_count[len(items)].append(label)
        ordered_labels = []
        for count in sorted(labels_by_count, reverse=True):
            labels = labels_by_count[count]
            rng.shuffle(labels)
            ordered_labels.extend(labels)

        chosen, labels, remaining = [], cycle(ordered_labels), min(len(rows), k)
        while remaining > 0:
            items = by_label[next(labels)]
            if items:
                chosen.append(items.pop(rng.randrange(len(items))))
                remaining -= 1
        shots[subject] = chosen
    return shots


def question_block(template: dict, row: dict, with_answer: bool = True) -> str:
    """One question with its options A–D, ending in the answer line."""
    block = f"{template['question']}: {row['question']}\n"
    block += "".join(f"{letter}. {choice}\n" for letter, choice in zip(LETTERS, row["choices"]))
    if with_answer:
        return block + f"{template['answer']}: {row['answer']}\n"
    return block + f"{template['answer']}:"


def build_prompt(template: dict, subject_name: str, shots: list[dict], item: dict) -> str:
    """HELM's MMLU prompt for one test question: the header, the examples, then the question."""
    header = template["header"].format(subject=subject_name) + "\n"
    examples = [question_block(template, shot) for shot in shots]
    return "\n".join([header, *examples, question_block(template, item, with_answer=False)])


def get_model_digest(model: str, host: str | None = None) -> str:
    """Return the digest of an installed Ollama model, which identifies its exact weights."""
    name = model if ":" in model else f"{model}:latest"
    for installed in ollama.Client(host=host).list().models:
        if installed.model == name:
            return installed.digest
    raise ValueError(f"Model {name} is not installed in Ollama.")


def git_state() -> dict:
    """Return the current commit and whether the working tree has uncommitted changes."""
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=HERE, capture_output=True, text=True, check=True
        ).stdout.strip()

    try:
        return {"commit": git("rev-parse", "--short", "HEAD"), "dirty": bool(git("status", "--porcelain"))}
    except (subprocess.CalledProcessError, FileNotFoundError):
        return {"commit": None, "dirty": None}


def build_manifest(
    experiment: int,
    model: str,
    model_digest: str | None,
    dataset: tuple[str, str, str],
    template: tuple[str, str, str],
    subjects: tuple[str, str, str],
    params: tuple[str, str, str],
    shots: dict[str, list[dict]],
    **extra,
) -> dict:
    """Build a run manifest to save next to eval outputs.

    dataset: (name, version, revision). template, subjects, params: (name, version, hash).
    The shots hash covers the selected example ids per subject, in order.
    Pass anything else worth recording as keyword args, e.g. description.
    """
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "experiment": experiment,
        "method": METHOD,
        "model": model,
        "model_digest": model_digest,
        "dataset": dict(zip(("name", "version", "revision"), dataset)),
        "template": dict(zip(("name", "version", "hash"), template)),
        "subjects": dict(zip(("name", "version", "hash"), subjects)),
        "params": dict(zip(("name", "version", "hash"), params)),
        "shots": {
            "per_subject": len(next(iter(shots.values()))),
            "hash": short_hash({subject: [row["id"] for row in rows] for subject, rows in shots.items()}),
        },
        "git": git_state(),
        **extra,
    }


def generate_run_id(manifest: dict) -> str:
    """Return a run id such as gemma3-4b_1a2b3c4d: the model name plus a hash of the run's settings."""
    model = re.sub(r"[^A-Za-z0-9.]+", "-", manifest["model"])
    return f"{model}_{short_hash({field: manifest[field] for field in RUN_ID_FIELDS})}"


def ask_model(client: ollama.Client, model: str, prompt: str, params: dict) -> dict:
    """Send one prompt as plain text, without the chat template; return the generated text and prompt length."""
    response = client.generate(model=model, prompt=prompt, raw=True, options=params)
    return {"response": response.response, "prompt_tokens": response.prompt_eval_count}


def parse_answer(response: str | None) -> str | None:
    """Return the letter the model generated, or None if it generated anything else."""
    letter = (response or "").strip()
    return letter if len(letter) == 1 and letter in LETTERS else None


def read_answers(path: Path) -> dict[str, dict]:
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


def summarize_answers(records: dict[str, dict], total: int) -> dict:
    """Count a run's results. Failed requests and invalid answers count as wrong in the accuracy."""
    asked = list(records.values())
    correct = sum(record["prediction"] == record["correct_answer"] for record in asked)
    return {
        "total": total,
        "asked": len(asked),
        "failed": sum(record["error"] is not None for record in asked),
        "invalid": sum(record["error"] is None and record["prediction"] is None for record in asked),
        "not_asked": total - len(asked),
        "correct": correct,
        "accuracy": correct / len(asked) if asked else 0.0,
    }


def run_experiment(
    manifest: dict,
    questions: list[dict],
    make_prompt,
    params: dict,
    host: str | None = None,
    retry_failed: bool = False,
) -> dict:
    """Ask every question, saving each answer as it arrives; a re-run continues where this one stopped.

    make_prompt turns a question row into its prompt. Results go to
    experiments/experiment_<number>/<run id>/: manifest.json and answers.jsonl, with one line per
    attempt. The same settings give the same run id, so they continue the same run; different
    settings start a new one.

    A failed request (an error, such as Ollama being down) keeps its failure and counts as wrong;
    pass retry_failed=True to ask it again. An invalid answer is the model's answer and is never
    asked again.
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
    failed = [
        question
        for question in questions
        if question["id"] in records and records[question["id"]]["error"] is not None
    ]
    to_retry = failed if retry_failed else []
    print(
        f"Experiment {manifest['experiment']}, run {run_id}: {len(questions) - len(not_asked) - len(failed)} done, "
        f"{len(not_asked)} not asked, {len(failed)} failed" + (" and will be retried." if retry_failed else ".")
    )

    client = ollama.Client(host=host, timeout=REQUEST_TIMEOUT)
    consecutive_failures = 0
    with open(answers_path, "a", encoding="utf-8") as answers_file:
        for position, question in enumerate(not_asked + to_retry):
            started = time.perf_counter()
            try:
                reply = ask_model(client, manifest["model"], make_prompt(question), params)
                error = None
            except Exception as exception:
                reply = {"response": None, "prompt_tokens": None}
                error = f"{type(exception).__name__}: {exception}"[:500]
            if reply["prompt_tokens"] is not None and reply["prompt_tokens"] >= params["num_ctx"] - CONTEXT_MARGIN:
                raise RuntimeError(
                    f"Question {question['id']} used {reply['prompt_tokens']} of {params['num_ctx']} context tokens, "
                    "so its prompt was probably cut. Add a params version with a larger num_ctx."
                )
            record = {
                "question_id": question["id"],
                "subject": question["subject"],
                "response": reply["response"],
                "prediction": parse_answer(reply["response"]),
                "correct_answer": question["answer"],
                "prompt_tokens": reply["prompt_tokens"],
                "error": error,
                "seconds": round(time.perf_counter() - started, 3),
            }
            answers_file.write(json.dumps(record, ensure_ascii=False) + "\n")
            answers_file.flush()
            records[question["id"]] = record

            summary = summarize_answers(records, len(questions))
            if (position + 1) % PROGRESS_EVERY == 0:
                print(f"{len(records)} / {len(questions)} questions, accuracy {summary['accuracy']:.2%}")

            consecutive_failures = consecutive_failures + 1 if error else 0
            if position < len(not_asked):
                if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                    raise RuntimeError(
                        f"Stopped after {consecutive_failures} failures in a row. Last error: {error}. "
                        "Fix the problem, then run again with retry_failed=True to ask the failed questions again."
                    )
                if len(records) == MIN_ACCURACY_AFTER and summary["accuracy"] < MIN_ACCURACY:
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
    for manifest_path in sorted((EXPERIMENTS_DIR / f"experiment_{experiment}").glob("*/manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        runs[manifest["run_id"]] = (
            manifest,
            list(read_answers(manifest_path.parent / "answers.jsonl").values()),
        )
    return runs
