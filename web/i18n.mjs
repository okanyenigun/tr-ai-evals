export const TEXT = {
  "TR": {
    "benchmark": "Test",
    "title": "Türkçe Yapay Zekâ Karşılaştırmaları",
    "intro": "Yapay zekâ modellerini Türkçe görevlerde değerlendiren özel testler.",
    "stats": "{models} model · {questions} soru · {courses} ders",
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
    "rows": "{count} satır",
    "empty": "Bu filtrelerle eşleşen sonuç yok. Filtreleri değiştirin veya sıfırlayın.",
    "all_models": "Tüm modeller",
    "all_courses": "Tüm dersler",
    "selected": "{count} seçili",
    "search": "Ara…",
    "loading": "Sonuçlar yükleniyor…",
    "error": "Sonuçlar yüklenemedi. Lütfen tekrar deneyin.",
    "retry": "Tekrar dene",
    "filters": "Filtreler",
    "tables": "Sonuç tabloları"
  },
  "EN": {
    "benchmark": "Benchmark",
    "title": "Turkish AI Benchmarks",
    "intro": "A collection of custom benchmarks evaluating AI models on Turkish-language tasks.",
    "stats": "{models} models · {questions} questions · {courses} courses",
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
    "rows": "{count} rows",
    "empty": "No results match these filters. Adjust or reset the filters.",
    "all_models": "All models",
    "all_courses": "All courses",
    "selected": "{count} selected",
    "search": "Search…",
    "loading": "Loading results…",
    "error": "The results could not be loaded. Please try again.",
    "retry": "Try again",
    "filters": "Filters",
    "tables": "Result tables"
  }
};

export const HEADERS_TR = {
  "Experiment": "Deney",
  "Model": "Model",
  "Course": "Ders",
  "Questions": "Soru sayısı",
  "Correct": "Doğru",
  "Incorrect": "Yanlış",
  "Invalid / missing": "Geçersiz / eksik",
  "Accuracy": "Doğruluk",
  "Valid-answer rate": "Geçerli yanıt oranı",
  "Accuracy among valid predictions": "Geçerli yanıtlarda doğruluk"
};

export const COURSE_LABELS = {
  "BİYOLOJİ": [
    "Biyoloji",
    "Biology"
  ],
  "COĞRAFYA": [
    "Coğrafya",
    "Geography"
  ],
  "EDEBİYAT": [
    "Edebiyat",
    "Literature"
  ],
  "FELSEFE_DİN": [
    "Felsefe ve Din",
    "Philosophy and Religion"
  ],
  "FEN": [
    "Fen",
    "Science"
  ],
  "FİZİK": [
    "Fizik",
    "Physics"
  ],
  "GEOMETRİ": [
    "Geometri",
    "Geometry"
  ],
  "KİMYA": [
    "Kimya",
    "Chemistry"
  ],
  "MATEMATİK": [
    "Matematik",
    "Mathematics"
  ],
  "SOSYAL_BİLİMLER": [
    "Sosyal Bilimler",
    "Social Sciences"
  ],
  "TARİH": [
    "Tarih",
    "History"
  ],
  "TÜRKÇE": [
    "Türkçe",
    "Turkish"
  ]
};

export function text(language, key, values = {}) {
  return Object.entries(values).reduce((message, [key, value]) => message.replaceAll(`{${key}}`, String(value)), TEXT[language][key]);
}

export function courseLabel(course, language) {
  return COURSE_LABELS[course]?.[language === "TR" ? 0 : 1] ?? course;
}

export function headerLabel(column, language, rate = false) {
  let label = language === "TR" ? (HEADERS_TR[column] ?? column.replace(/^Exp /, "Deney ")) : column;
  return label + (rate ? " (%)" : "");
}
