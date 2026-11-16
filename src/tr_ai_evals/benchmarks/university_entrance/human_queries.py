"""Human message builders. Never edit a published version; add a new one."""

import re
from collections.abc import Callable

LABELLED_PHRASE = re.compile(r"(?:^|\s)(?:I|II|III|IV|V)(?:,|$)")


def format_underline_note_v1(underlined_text: str) -> str:
    """Render underlined_text as a one-line note.

    In this field "-\\n" is a word split across booklet lines; other line breaks separate phrases.
    """
    phrases = [
        p.strip() for p in underlined_text.replace("-\n", "").split("\n") if p.strip()
    ]
    if len(phrases) == 1:
        # Several phrases can share a line, separated by ";" or labelled I-V. Those stay
        # as written because the labels may be the only link to the options.
        several = ";" in phrases[0] or len(LABELLED_PHRASE.findall(phrases[0])) > 1
        wording = "şu ifadeler" if several else "şu ifade"
        return f"Not: Soru kitapçığında {wording} altı çizilidir: {phrases[0]}"
    quoted = ", ".join(f'"{p}"' for p in phrases)
    return f"Not: Soru kitapçığında şu ifadeler altı çizilidir: {quoted}"


def build_human_query_v1(question_data: dict) -> str:
    """Render one dataset row as the human message sent to the LLM."""
    parts = [
        f"Soru ID: {question_data['id']}",
        f"Ders: {question_data['course'].replace('_', ' ')}",
    ]

    # Başka bir metne/soru grubuna bağlıysa önce gerekli bağlamı ver.
    # Bazı satırlarda soru metni bu bağlamla başlar; o zaman tekrar etme.
    context = (question_data.get("dependent_text") or "").strip()
    if (
        question_data.get("has_dependency")
        and context
        and context not in question_data["question_text"]
    ):
        parts.extend(
            [
                "",
                "Bağlı metin / bağlam:",
                context,
            ]
        )

    parts.extend(
        [
            "",
            "Soru:",
            question_data["question_text"].strip(),
        ]
    )

    # Kitapçıkta altı çizili olan kısmı ayrıca belirt.
    if question_data.get("underlined_text"):
        parts.extend(
            [
                "",
                format_underline_note_v1(question_data["underlined_text"]),
            ]
        )

    # Görsel / matematiksel ifade bilgileri
    if question_data.get("has_image"):
        parts.extend(
            [
                "",
                "Not: Bu soru bir görsel içermektedir. Soruyu yanıtlarken verilen görseli de dikkate al.",
            ]
        )
    elif question_data.get("image"):
        # has_expression satırlarında görsel, sorunun kitapçıktaki kırpılmış hâlidir.
        parts.extend(
            [
                "",
                "Not: Sorunun kitapçıktaki görüntüsü de ektedir; soruyu yanıtlarken dikkate al.",
            ]
        )

    if question_data.get("has_expression"):
        parts.extend(
            [
                "",
                (
                    "Not: Soruda matematiksel veya bilimsel ifade/formül varsa "
                    "bunları sorunun bir parçası olarak dikkate al."
                ),
            ]
        )

    # Cevap seçenekleri
    parts.extend(
        [
            "",
            "Seçenekler:",
        ]
    )

    for answer in question_data["answers"]:
        parts.append(f"{answer['code']}) {answer['text'].strip()}")

    return "\n".join(parts)


HUMAN_QUERIES: dict[tuple[str, str], Callable[[dict], str]] = {
    ("tr_uni_exam_human_query", "v1"): build_human_query_v1,
}


def _reference_row(**overrides) -> dict:
    row = {
        "id": 1,
        "course": "SOSYAL_BİLİMLER",
        "question_text": "Soru metni?",
        "answers": [{"code": code, "text": f"Seçenek {code}"} for code in "ABCDE"],
        "has_image": False,
        "has_expression": False,
        "has_dependency": False,
        "dependent_text": None,
        "underlined_text": None,
        "image": None,
    }
    return {**row, **overrides}


# A builder's hash covers what it renders for these rows. They exercise every branch of a
# builder. Never edit them: any change here changes the hash of every version.
REFERENCE_ROWS = [
    _reference_row(),
    _reference_row(
        question_text="  Soru metni?\n",
        answers=[{"code": "A", "text": "  Seçenek A \n"}],
    ),
    _reference_row(has_dependency=True, dependent_text=" Parça. "),
    _reference_row(has_dependency=True, dependent_text=None),
    _reference_row(has_dependency=False, dependent_text="Parça."),
    _reference_row(
        has_dependency=True,
        dependent_text="Parça.",
        question_text="Parça.\n\nSoru metni?",
    ),
    _reference_row(underlined_text=" metni "),
    _reference_row(underlined_text="özdeş\nkesinlikle yanlıştır?"),
    _reference_row(underlined_text="azal-\nmasını"),
    _reference_row(underlined_text=" bir \n\n iki\n"),
    _reference_row(underlined_text="ayrılan I; göz ardı etmeyen II"),
    _reference_row(underlined_text="acılı I, buruk II, yorgun III"),
    _reference_row(underlined_text="Seyfiye, İlmiye, Kalemiye"),
    _reference_row(has_image=True, image="b64"),
    _reference_row(has_image=True, image=None),
    _reference_row(image="b64"),
    _reference_row(has_expression=True),
    _reference_row(has_expression=True, image="b64"),
    _reference_row(
        has_dependency=True,
        dependent_text="Parça.",
        underlined_text="metni",
        has_image=True,
        has_expression=True,
        image="b64",
    ),
]
