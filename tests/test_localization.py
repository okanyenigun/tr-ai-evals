import unittest

import pandas as pd

from tr_ai_evals.explorer.localization import localized_table


class LocalizationTests(unittest.TestCase):
    def test_translation_preserves_numeric_values_and_source(self):
        source = pd.DataFrame(
            {
                "Course": ["KİMYA", "BİYOLOJİ"],
                "Model": ["gemma3:27b", "qwen3.8:27b"],
                "Accuracy (%)": [21.45, 95.14],
            }
        )
        original = source.copy(deep=True)
        for language, accuracy_column in (
            ("TR", "Doğruluk (%)"),
            ("EN", "Accuracy (%)"),
        ):
            translated = localized_table(source, language)
            pd.testing.assert_series_equal(
                translated[accuracy_column], source["Accuracy (%)"], check_names=False
            )
            pd.testing.assert_series_equal(translated["Model"], source["Model"])
        pd.testing.assert_frame_equal(source, original)

    def test_course_sort_uses_visible_names(self):
        source = pd.DataFrame(
            {"Course": ["GEOMETRİ", "KİMYA"], "Questions": [291, 275]}
        )
        ascending = localized_table(source, "EN", sort_by="Course")
        self.assertEqual(ascending["Course"].tolist(), ["Chemistry", "Geometry"])
        self.assertEqual(ascending["Questions"].tolist(), [275, 291])
        descending = localized_table(source, "EN", sort_by="Course", ascending=False)
        self.assertEqual(descending["Course"].tolist(), ["Geometry", "Chemistry"])


if __name__ == "__main__":
    unittest.main()
