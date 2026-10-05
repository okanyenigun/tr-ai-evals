"""Turkish and English presentation strings; source identifiers stay unchanged."""

TEXT = {
    "TR": {
        "benchmark": "Test",
        "title": "Türkçe Yapay Zekâ Karşılaştırmaları",
        "intro": "Yapay zekâ modellerini Türkçe görevlerde değerlendiren özel testler.",
        "stats": "**{models} model · {questions} soru · {courses} ders**",
        "overall": "Genel karşılaştırma",
        "course_accuracy": "Ders bazında doğruluk",
        "models": "Modeller",
        "models_help": "Tüm modelleri dahil etmek için boş bırakın.",
        "courses": "Dersler",
        "courses_help": "Tüm dersleri dahil etmek için boş bırakın.",
        "minimum": "En düşük doğruluk (%)",
        "sort": "Sıralama ölçütü",
        "sort_courses": "Dersleri sırala",
        "sort_courses_help": "Dersleri bir modelin doğruluğuna göre sıralamak için modeli seçin.",
        "order": "Sıralama yönü",
        "descending": "Azalan",
        "ascending": "Artan",
        "results": "Test sonuçları",
        "reset": "Filtreleri sıfırla",
        "download": "Filtrelenmiş CSV'yi indir",
        "rows": "**{count} satır**",
        "empty": "**Bu filtrelerle eşleşen sonuç yok.** Filtreleri değiştirin veya sıfırlayın.",
    },
    "EN": {
        "benchmark": "Benchmark",
        "title": "Turkish AI Benchmarks",
        "intro": "A collection of custom benchmarks evaluating AI models on Turkish-language tasks.",
        "stats": "**{models} models · {questions} questions · {courses} courses**",
        "overall": "Overall comparison",
        "course_accuracy": "Course accuracy",
        "models": "Models",
        "models_help": "Leave empty to include all models.",
        "courses": "Courses",
        "courses_help": "Leave empty to include all courses.",
        "minimum": "Minimum accuracy (%)",
        "sort": "Sort by",
        "sort_courses": "Sort courses by",
        "sort_courses_help": "Choose a model to sort courses by its accuracy.",
        "order": "Order",
        "descending": "Descending",
        "ascending": "Ascending",
        "results": "Benchmark results",
        "reset": "Reset filters",
        "download": "Download filtered CSV",
        "rows": "**{count} rows**",
        "empty": "**No results match these filters.** Adjust or reset the filters.",
    },
}

HEADERS_TR = {
    "Experiment": "Deney",
    "Model": "Model",
    "Course": "Ders",
    "Questions": "Soru sayısı",
    "Correct": "Doğru",
    "Incorrect": "Yanlış",
    "Invalid / missing": "Geçersiz / eksik",
    "Accuracy": "Doğruluk",
    "Valid-answer rate": "Geçerli yanıt oranı",
    "Accuracy among valid predictions": "Geçerli yanıtlarda doğruluk",
}

COURSE_LABELS = {
    "BİYOLOJİ": ("Biyoloji", "Biology"),
    "COĞRAFYA": ("Coğrafya", "Geography"),
    "EDEBİYAT": ("Edebiyat", "Literature"),
    "FELSEFE_DİN": ("Felsefe ve Din", "Philosophy and Religion"),
    "FEN": ("Fen", "Science"),
    "FİZİK": ("Fizik", "Physics"),
    "GEOMETRİ": ("Geometri", "Geometry"),
    "KİMYA": ("Kimya", "Chemistry"),
    "MATEMATİK": ("Matematik", "Mathematics"),
    "SOSYAL_BİLİMLER": ("Sosyal Bilimler", "Social Sciences"),
    "TARİH": ("Tarih", "History"),
    "TÜRKÇE": ("Türkçe", "Turkish"),
}


def text(key: str, language: str = "TR") -> str:
    return TEXT[language][key]


def header_label(column: str, language: str) -> str:
    if language == "EN":
        return column
    if column.startswith("Exp "):
        return column.replace("Exp ", "Deney ", 1)
    suffix = " (%)" if column.endswith(" (%)") else ""
    name = column.removesuffix(suffix) if suffix else column
    return HEADERS_TR.get(name, name) + suffix


def course_label(course: str, language: str) -> str:
    labels = COURSE_LABELS.get(course, (course, course))
    return labels[0 if language == "TR" else 1]


def localized_table(
    table, language: str, *, sort_by: str | None = None, ascending=True
):
    result = table.copy()
    if "Course" in result:
        result["Course"] = result["Course"].map(
            lambda value: course_label(value, language)
        )
        if sort_by == "Course":
            result = result.sort_values("Course", ascending=ascending, kind="stable")
    return result.rename(
        columns=lambda column: header_label(column, language)
    ).reset_index(drop=True)


def row_summary(count: int, language: str) -> str:
    if not count:
        return text("empty", language)
    if language == "EN" and count == 1:
        return "**1 row**"
    return text("rows", language).format(count=count)
