"""Load, filter, and export benchmark results independently of the interface."""

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd

RATE_COLUMNS = ["Accuracy", "Valid-answer rate", "Accuracy among valid predictions"]


def load_table(path: Path) -> pd.DataFrame:
    """Read a benchmark table, retaining source column order and numeric values."""
    with path.open(encoding="utf-8") as source:
        return pd.DataFrame(json.load(source))


def select_rows(
    table: pd.DataFrame,
    models: list[str] | None = None,
    courses: list[str] | None = None,
) -> pd.DataFrame:
    """Select models and courses; empty selections mean all available values."""
    result = table.copy()
    if models:
        result = result[result["Model"].isin(models)]
    if courses:
        result = result[result["Course"].isin(courses)]
    return result


def display_table(table: pd.DataFrame, rate_columns: list[str]) -> pd.DataFrame:
    """Convert rates to numeric percentages on a copy for display and export."""
    result = table.copy()
    for column in rate_columns:
        result[column] = (result[column] * 100).round(2)
    return result.rename(
        columns={column: f"{column} (%)" for column in rate_columns}
    ).reset_index(drop=True)


@dataclass
class BenchmarkResults:
    """The three result tables for one benchmark, loaded from an explicit directory."""

    overall: pd.DataFrame
    course_accuracy: pd.DataFrame
    detailed: pd.DataFrame

    @classmethod
    def from_directory(cls, directory: Path) -> "BenchmarkResults":
        return cls(
            overall=load_table(directory / "overall_comparison.json"),
            course_accuracy=load_table(directory / "course_accuracy_comparison.json"),
            detailed=load_table(directory / "course_detailed_metrics.json"),
        )

    @property
    def models(self) -> list[str]:
        return self.overall["Model"].tolist()

    @property
    def courses(self) -> list[str]:
        return self.course_accuracy["Course"].tolist()

    @property
    def experiment_columns(self) -> dict[str, str]:
        return {
            row["Model"]: f"Exp {row['Experiment']}: {row['Model']}"
            for row in self.overall.to_dict("records")
        }

    def overall_results(
        self,
        models: list[str] | None = None,
        minimum_accuracy: float = 0,
        sort_by: str = "Accuracy",
        order: str = "Highest first",
    ) -> pd.DataFrame:
        table = select_rows(self.overall, models)
        table = table[table["Accuracy"] >= minimum_accuracy / 100]
        table = table.sort_values(
            sort_by, ascending=order == "Lowest first", kind="stable"
        )
        return display_table(table.drop(columns="Questions"), RATE_COLUMNS)

    def course_results(
        self,
        courses: list[str] | None = None,
        models: list[str] | None = None,
        sort_by: str = "Course",
        order: str = "Lowest first",
    ) -> pd.DataFrame:
        table = select_rows(self.course_accuracy, courses=courses)
        experiment_columns = self.experiment_columns
        sort_column = experiment_columns.get(sort_by, sort_by)
        table = table.sort_values(
            sort_column, ascending=order == "Lowest first", kind="stable"
        )
        columns = [
            experiment_columns[model]
            for model in self.models
            if not models or model in models
        ]
        return display_table(table[["Course", "Questions", *columns]], columns)

    def detailed_results(
        self,
        models: list[str] | None = None,
        courses: list[str] | None = None,
        minimum_accuracy: float = 0,
        sort_by: str = "Accuracy",
        order: str = "Highest first",
    ) -> pd.DataFrame:
        table = select_rows(self.detailed, models, courses)
        table = table[table["Accuracy"] >= minimum_accuracy / 100]
        table = table.sort_values(
            sort_by, ascending=order == "Lowest first", kind="stable"
        )
        return display_table(table, RATE_COLUMNS)


def csv_download(table: pd.DataFrame, name: str) -> str:
    """Write an isolated CSV with a UTF-8 BOM for spreadsheet compatibility."""
    with NamedTemporaryFile(prefix=f"{name}-", suffix=".csv", delete=False) as output:
        path = output.name
    table.to_csv(path, index=False, encoding="utf-8-sig")
    return path
