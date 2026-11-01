# Turkish University Entrance Exam Benchmark

**Dataset:** [`yeniguno/turkish-university-entrance-exam-questions`](https://huggingface.co/datasets/yeniguno/turkish-university-entrance-exam-questions), version `v1` (revision `078b264`), 4,858 questions

## Intended use

This benchmark helps people choose a model for Turkish-language work. It measures academic knowledge and reasoning on exam questions, not everyday Turkish use such as writing or summarizing.

## Scenario

| Axis | Definition |
|---|---|
| **Task** | Multiple-choice question answering: select the one correct option (A–E). 2,242 questions include an image. |
| **What** | National university entrance exam questions from 118 exam papers, across 12 course labels: BİYOLOJİ, COĞRAFYA, EDEBİYAT, FELSEFE_DİN, FEN, FİZİK, GEOMETRİ, KİMYA, MATEMATİK, SOSYAL_BİLİMLER, TARİH, TÜRKÇE. |
| **When** | 2006–2017: ÖSS 2006–2009 (923 questions), YGS 2010–2017 (1,291) and LYS 2010–2017 (2,644). |
| **Who** | Written by ÖSYM for candidates applying to Turkish universities. |
| **Language** | Turkish. Original exam text, not translated. |

## Course and image use

Course and image use are tangled together. Of the 4,858 questions, 2,242 (46%) include an image and 2,616 are text only:

- **1,040 questions** are marked as having a visual.
- **1,202 questions** contain an expression and attach their cropped booklet image.

The share of questions with an image varies widely by course:

| Image use | Courses (share of questions with an image) |
|---|---|
| **High** | GEOMETRİ 99%, MATEMATİK 94%, KİMYA 89%, FİZİK 85% |
| **Mixed** | FEN 68%, BİYOLOJİ 43%, COĞRAFYA 33%, FELSEFE_DİN 12%, SOSYAL_BİLİMLER 11% |
| **Low** | TARİH 2%, TÜRKÇE 2%, EDEBİYAT 2% |

A course score therefore reflects both subject knowledge and the ability to read images. Differences between courses shouldn't be read as differences in subject knowledge alone.

## Training data overlap

All questions come from public exams held in 2006–2017, so they may appear in models' training data. Scores may partly reflect memorized questions rather than reasoning. This hasn't been measured.

## Prompt setup

All models are tested with the same setup, v1, which isn't tuned for any model:

- **Prompts:** the [system prompt](prompts/tr_uni_exam_system_v1.txt) and [question format](human_queries.py), with no example questions.
- **Answer:** a question ID and a letter, with no explanation, using the [answer schema](schemas.py).
- **Settings:** [temperature 0](params/tr_uni_exam_params_v1.json).

Scores describe each model under this setup. How much the setup itself affects scores hasn't been tested.

## Metrics

A metric that isn't measured yet says nothing about how a model would perform on it.

| Metric | Status | Notes |
|---|---|---|
| **Accuracy** | Published | Share of questions answered correctly, with invalid or missing answers counted as incorrect. Accuracy among valid answers is also published. |
| **Valid-answer rate** | Published | Share of questions with a valid answer. |
| **Efficiency** | Published | Time per question. |
| **Calibration** | Not yet measured | Needs each model's confidence in its answer. |
| **Robustness** | Not yet measured | Needs runs on slightly altered questions. |

## Future work

### Prompt setup study

A future study will compare:

- answer only vs reasoning allowed
- structured output vs a plain letter
- answers with vs without the question ID

### Calibration

Measure whether each model knows when it's unsure, using its confidence in each answer.

### Robustness

Measure whether answers hold when a question changes slightly without changing its meaning, using Turkish-specific changes such as typing without Turkish characters.
