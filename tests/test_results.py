import unittest
from pathlib import Path

import pandas as pd

from tr_ai_evals.explorer.results import BenchmarkResults, csv_download

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "university_entrance"


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.results = BenchmarkResults.from_directory(DATA_DIR)

    def test_all_rows_displayed(self):
        self.assertEqual(len(self.results.overall_results()), 10)
        self.assertEqual(len(self.results.course_results()), 12)
        self.assertEqual(len(self.results.detailed_results()), 120)

    def test_overall_filters_and_numeric_sorting(self):
        result = self.results.overall_results(
            [self.results.models[0], self.results.models[2], self.results.models[8]], 80
        )
        self.assertEqual(
            result["Model"].tolist(), [self.results.models[8], self.results.models[2]]
        )
        self.assertEqual(result["Accuracy (%)"].tolist(), [89.74, 89.66])
        self.assertNotIn("Questions", result)

    def test_combined_detail_filters(self):
        result = self.results.detailed_results(
            [self.results.models[2]],
            [self.results.courses[0], self.results.courses[1]],
            90,
        )
        self.assertEqual(result["Course"].tolist(), [self.results.courses[0]])
        self.assertEqual(result["Model"].tolist(), [self.results.models[2]])

    def test_course_columns_and_sort(self):
        result = self.results.course_results(
            models=[self.results.models[2]],
            sort_by=self.results.models[2],
            order="Highest first",
        )
        self.assertEqual(result.shape, (12, 3))
        self.assertTrue(result.iloc[:, -1].is_monotonic_decreasing)
        self.assertEqual(result.iloc[0]["Course"], "MATEMATİK")

    def test_empty_results_keep_headers(self):
        result = self.results.overall_results(minimum_accuracy=100)
        self.assertTrue(result.empty)
        self.assertIn("Accuracy (%)", result)

    def test_queries_do_not_mutate_source(self):
        original = self.results.detailed.copy(deep=True)
        self.results.detailed_results(
            [self.results.models[2]], [self.results.courses[0]], 50
        )
        pd.testing.assert_frame_equal(self.results.detailed, original)
        self.assertTrue(self.results.overall["Accuracy"].between(0, 1).all())

    def test_sort_every_supported_column(self):
        for column in self.results.detailed:
            result = self.results.detailed_results(sort_by=column, order="Lowest first")
            label = column if column in result else f"{column} (%)"
            self.assertTrue(result[label].is_monotonic_increasing, column)

    def test_download_matches_filtered_rows_and_turkish_text(self):
        table = self.results.detailed_results([self.results.models[2]], ["BİYOLOJİ"])
        path = Path(csv_download(table, "test"))
        try:
            pd.testing.assert_frame_equal(pd.read_csv(path), table)
        finally:
            path.unlink()

    def test_course_totals_match_overall_counts(self):
        columns = ["Questions", "Correct", "Incorrect", "Invalid / missing"]
        totals = self.results.detailed.groupby(["Experiment", "Model"])[columns].sum()
        overall = self.results.overall.set_index(["Experiment", "Model"])[columns]
        pd.testing.assert_frame_equal(totals.sort_index(), overall.sort_index())

    def test_course_comparison_matches_detailed_results(self):
        comparison = self.results.course_accuracy.set_index("Course")
        self.assertFalse(
            self.results.detailed.duplicated(["Course", "Experiment"]).any()
        )
        for row in self.results.detailed.to_dict("records"):
            with self.subTest(course=row["Course"], experiment=row["Experiment"]):
                column = self.results.experiment_columns[row["Model"]]
                self.assertEqual(
                    comparison.loc[row["Course"], "Questions"], row["Questions"]
                )
                self.assertAlmostEqual(
                    comparison.loc[row["Course"], column], row["Accuracy"]
                )

    def test_reported_metrics_match_counts(self):
        for table in (self.results.overall, self.results.detailed):
            questions = table["Questions"]
            correct = table["Correct"]
            valid = questions - table["Invalid / missing"]
            pd.testing.assert_series_equal(
                questions, correct + table["Incorrect"], check_names=False
            )
            for column, expected in (
                ("Accuracy", correct / questions),
                ("Valid-answer rate", valid / questions),
                ("Accuracy among valid predictions", correct / valid),
            ):
                with self.subTest(metric=column, rows=len(table)):
                    pd.testing.assert_series_equal(
                        table[column],
                        expected,
                        check_names=False,
                        rtol=1e-12,
                        atol=1e-12,
                    )


if __name__ == "__main__":
    unittest.main()
