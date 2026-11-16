"""Write the result tables the Hugging Face Space reads, from an experiment's saved runs.

Usage: uv run src/tr_ai_evals/benchmarks/university_entrance/export_space_data.py

Writes overall_comparison.json and course_accuracy_comparison.json to data/university_entrance/
at the repository root. Invalid answers count as incorrect, as in the benchmark report.
"""

import json
from pathlib import Path

from funcs import load_experiment, load_train_data

EXPERIMENT = 1
DATASET_NAME = "tr_uni_exam_questions"
DATASET_VERSION = "v1"
OUTPUT_DIR = Path(__file__).resolve().parents[4] / "data" / "university_entrance"


def is_correct(record: dict) -> bool:
    return (
        record["llm_answer"] is not None
        and record["llm_answer"]["code"] == record["correct_answer"]
    )


def main() -> None:
    questions, _ = load_train_data(name=DATASET_NAME, version=DATASET_VERSION)
    course_of = {question["id"]: question["course"] for question in questions}

    runs = []
    for manifest, records in load_experiment(EXPERIMENT).values():
        if manifest["dataset"]["version"] != DATASET_VERSION or len(records) < len(
            questions
        ):
            print(f"Skipping {manifest['model']}: not a complete {DATASET_VERSION} run.")
            continue
        by_id = {record["question_id"]: record for record in records}
        total = len(by_id)
        correct = sum(map(is_correct, by_id.values()))
        valid = sum(record["llm_answer"] is not None for record in by_id.values())
        row = {
            "Experiment": manifest["experiment"],
            "Model": manifest["model"],
            "Questions": total,
            "Correct": correct,
            "Incorrect": total - correct,
            "Invalid / missing": total - valid,
            "Accuracy": correct / total,
            "Valid-answer rate": valid / total,
            "Accuracy among valid predictions": correct / valid if valid else 0.0,
        }
        runs.append((row, by_id))
    runs.sort(key=lambda run: -run[0]["Accuracy"])

    course_rows = []
    for course in sorted(set(course_of.values())):
        ids = [question_id for question_id, label in course_of.items() if label == course]
        course_row = {"Course": course, "Questions": len(ids)}
        for row, by_id in runs:
            column = f"Exp {row['Experiment']}: {row['Model']}"
            course_row[column] = sum(is_correct(by_id[question_id]) for question_id in ids) / len(ids)
        course_rows.append(course_row)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, table in (
        ("overall_comparison.json", [row for row, _ in runs]),
        ("course_accuracy_comparison.json", course_rows),
    ):
        (OUTPUT_DIR / name).write_text(
            json.dumps(table, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"Wrote {len(runs)} models and {len(course_rows)} courses to {OUTPUT_DIR}.")


if __name__ == "__main__":
    main()
