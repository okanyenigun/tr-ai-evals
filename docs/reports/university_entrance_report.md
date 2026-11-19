# Turkish University Entrance Exam Benchmark: Report

**Date:** 2026-11-16

## 1. Summary

Ten models, all run locally, answered all 4,858 questions from Turkish university entrance exams held in 2006–2017.

- **Top three:** `gemma4:31b` scored highest at 92.18%, ahead of `muse-glimmer:30b` (90.90%) and `qwen3.8:27b` (90.72%).
- **Thinking support:** the five models that support thinking all scored above 75%, and the five that don't all scored below 57%. The two groups also differ in family and size, so this shows a link, not that thinking causes the gap.
- **Speed:** the thinking-capable models took 2–10 seconds per question at the median, against under 1 second for the others.
- **Visual questions:** within the same course, nearly every model scored lower on questions with a visual, such as a diagram or map, than on text-only ones, by up to 36 points. Expressions rendered as images cost little: in MATEMATİK, models score about the same on them as on text-only questions.
- **Main caveats:** all results come from one prompt setup that doesn't control thinking. Visual and text-only questions may also differ in difficulty, not only in format.

## 2. Benchmark

- **Purpose:** Turkish academic knowledge and reasoning, measured with real exam questions
- **Task:** choose the one correct option (A–E) for a multiple-choice question, some with an image
- **Domain and language:** national university entrance exams (ÖSS, YGS, LYS) across 12 course labels, 2006–2017, in Turkish
- **Intended use:** comparing models on Turkish academic question answering, as one input when choosing a model for Turkish-language work
- **Out of scope:**
  - general Turkish proficiency, such as conversation, following instructions, writing, summarizing or understanding documents
  - comparison with human candidates' exam scores

## 3. Data

- **Source:** ÖSYM exam papers, via [`yeniguno/turkish-university-entrance-exam-questions`](https://huggingface.co/datasets/yeniguno/turkish-university-entrance-exam-questions)
- **Version:** `v1`, revision `078b264`
- **Size:** 4,858 questions from 118 exam papers, in one split, all used
- **Composition:**
  - 12 course labels, with question counts shown in section 7.2
  - by exam: ÖSS 2006–2009 (923 questions), YGS 2010–2017 (1,291) and LYS 2010–2017 (2,644)
  - three question types:
    - **text only:** 2,616 questions, mostly EDEBİYAT, TARİH, TÜRKÇE, FELSEFE_DİN and COĞRAFYA
    - **expression:** 1,202 questions with a cropped booklet image because they contain a mathematical or scientific expression, mostly MATEMATİK (687), KİMYA (166) and FEN (103)
    - **visual:** 1,040 questions with a visual such as a diagram, graph or map, mostly GEOMETRİ (214), FEN (182), FİZİK (181), MATEMATİK (158) and COĞRAFYA (118). Questions with both a visual and an expression count as visual.
  - a balanced answer key, with 958–994 questions per letter
- **Known issues:**
  - **Course and image use are tangled.** 85–99% of GEOMETRİ, MATEMATİK, KİMYA and FİZİK questions include an image, against 2% for EDEBİYAT, TARİH and TÜRKÇE. A course score therefore reflects both subject knowledge and the ability to read images.
  - **Questions may be in training data.** All questions come from public exams held in 2006–2017, so models may have seen them during training. Scores, even very high ones, may partly reflect memorized questions rather than reasoning, and this hasn't been measured.

## 4. Evaluation method

- **Prompting:** zero-shot, in Turkish, with the same setup (v1) for every model and no tuning for any of them:
  - **System prompt:** tells the model it answers Turkish university entrance exam questions, and asks for only the question ID and a letter, with no explanation
  - **Question message:** the question ID, course, a linked passage when the question depends on one, the question text, notes on underlined text, images and expressions, then options A–E
  - **Images:** attached to the question message as PNG
- **Generation settings:**
  - temperature 0
  - no output length limit
  - thinking isn't set, so each model's default applies
  - context length was left at Ollama's default, observed at 32,768 tokens during the `gemma4:31b` run
- **Output format:** a JSON answer with the question ID and a letter A–E, enforced through a schema
- **Scoring:** the letter is compared with the answer key, and the ID isn't used
- **Metrics:**

| Metric | Definition | Direction |
|---|---|---|
| **Accuracy** (primary) | Correct answers ÷ all 4,858 questions | Higher is better |
| **Valid-answer rate** | Questions with a valid answer ÷ all questions | Higher is better |
| **Accuracy among valid answers** | Correct answers ÷ valid answers | Higher is better |
| **Time per question** | Wall-clock seconds per request, including any thinking | Lower is better |

- **Invalid outputs:** an answer that can't be parsed counts as wrong and isn't asked again. Every model got one attempt per question.
- **Baselines:**
  - random guessing: 20.00%
  - always choosing the most common letter (D): 20.46%

## 5. Models

All models use 4-bit quantization (Q4_K_M) and were run through Ollama.

| Model | Version (digest) | Size | Access | Modality | Notes |
|---|---|---|---|---|---|
| `gemma4:31b` | `6316f0629137` | 31.3B | Open weights | Text, image | Supports thinking |
| `muse-glimmer:30b` | `de878ce33ad8` | 27.9B | Open weights | Text, image | Supports thinking |
| `qwen3.8:27b` | `aaee06c39dcf` | 27.3B | Open weights | Text, image | Supports thinking |
| `ornith-1.5:35b` | `9f3b89b25219` | 35.5B | Open weights | Text, image | Supports thinking; mixture of experts |
| `gemma4:e4b` | `c6eb396dbd59` | 8.0B | Open weights | Text, image, audio | Supports thinking |
| `gemma3:27b` | `a418f5838eaf` | 27.4B | Open weights | Text, image | |
| `ministral-3:14b` | `4760c35aeb9d` | 13.9B | Open weights | Text, image | |
| `mistral-small3.2:latest` | `5a408ab55df5` | 24.0B | Open weights | Text, image | |
| `gemma3:12b` | `f4031aab637d` | 12.2B | Open weights | Text, image | |
| `gemma3:4b` | `a2af6cc3eb7f` | 4.3B | Open weights | Text, image | |

## 6. Run environment

- **Run date:** 2026-11-16
- **Hardware:** NVIDIA GeForce RTX 5090 (32 GB), AMD Ryzen 7 9800X3D, 46 GiB RAM, Ubuntu 24.04.5
- **Software:** Ollama 0.34.2 (at the time of writing), Python 3.12.3, `langchain-ollama` 1.1.0, `langchain-core` 1.7.3, `ollama` 0.6.3
- **Code version:** `a9ae970`

## 7. Results

### 7.1 Overall

| Model | Accuracy | Valid-answer rate | Accuracy among valid answers |
|---|---:|---:|---:|
| `gemma4:31b` | 92.18% | 98.41% | 93.66% |
| `muse-glimmer:30b` | 90.90% | 99.71% | 91.16% |
| `qwen3.8:27b` | 90.72% | 99.67% | 91.02% |
| `ornith-1.5:35b` | 86.52% | 93.33% | 92.70% |
| `gemma4:e4b` | 75.36% | 99.98% | 75.38% |
| `gemma3:27b` | 56.75% | 100.00% | 56.75% |
| `ministral-3:14b` | 55.39% | 100.00% | 55.39% |
| `mistral-small3.2:latest` | 51.61% | 100.00% | 51.61% |
| `gemma3:12b` | 51.05% | 100.00% | 51.05% |
| `gemma3:4b` | 30.03% | 100.00% | 30.03% |

### 7.2 By category

**Accuracy by course**, with question counts in the headers:

| Model | BİYOLOJİ (242) | COĞRAFYA (415) | EDEBİYAT (525) | FELSEFE_DİN (373) | FEN (420) | FİZİK (286) | GEOMETRİ (290) | KİMYA (272) | MATEMATİK (899) | SOSYAL_BİLİMLER (241) | TARİH (459) | TÜRKÇE (436) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gemma4:31b` | 95.45% | 87.95% | 88.00% | 96.25% | 88.81% | 79.72% | 88.62% | 96.32% | 96.66% | 93.78% | 95.64% | 93.35% |
| `muse-glimmer:30b` | 94.63% | 85.54% | 78.48% | 91.42% | 91.67% | 86.01% | 95.86% | 96.69% | 98.33% | 89.63% | 91.94% | 88.30% |
| `qwen3.8:27b` | 95.45% | 86.99% | 76.19% | 94.10% | 94.52% | 87.06% | 94.48% | 96.32% | 97.89% | 91.29% | 89.76% | 84.86% |
| `ornith-1.5:35b` | 93.80% | 82.89% | 66.67% | 90.35% | 89.05% | 82.17% | 90.34% | 95.22% | 97.11% | 87.14% | 86.06% | 77.29% |
| `gemma4:e4b` | 79.75% | 72.29% | 60.95% | 80.97% | 73.10% | 59.09% | 66.55% | 84.93% | 88.99% | 76.35% | 73.86% | 74.08% |
| `gemma3:27b` | 71.07% | 64.82% | 66.48% | 78.82% | 52.62% | 37.41% | 28.62% | 51.10% | 29.59% | 75.93% | 80.39% | 69.95% |
| `ministral-3:14b` | 66.53% | 64.58% | 54.48% | 76.68% | 53.57% | 40.91% | 26.90% | 55.15% | 33.37% | 74.69% | 77.78% | 64.91% |
| `mistral-small3.2:latest` | 59.92% | 63.86% | 51.05% | 75.34% | 51.43% | 36.36% | 25.17% | 55.51% | 26.59% | 70.54% | 73.42% | 59.17% |
| `gemma3:12b` | 59.50% | 60.72% | 55.62% | 73.99% | 49.05% | 33.92% | 27.59% | 43.75% | 25.81% | 69.29% | 74.51% | 62.61% |
| `gemma3:4b` | 26.45% | 31.81% | 27.43% | 44.24% | 26.90% | 26.92% | 21.72% | 28.68% | 22.14% | 44.40% | 37.91% | 32.80% |

**Accuracy by question type**, across all courses. Each type has a different course mix (section 3), so these columns compare subjects as well as formats.

| Model | Text only (2,616) | Expression (1,202) | Visual (1,040) |
|---|---:|---:|---:|
| `gemma4:31b` | 94.00% | 98.50% | 80.29% |
| `muse-glimmer:30b` | 89.11% | 98.09% | 87.12% |
| `qwen3.8:27b` | 88.57% | 97.75% | 87.98% |
| `ornith-1.5:35b` | 83.14% | 97.59% | 82.21% |
| `gemma4:e4b` | 76.11% | 92.01% | 54.23% |
| `gemma3:27b` | 73.85% | 38.35% | 35.00% |
| `ministral-3:14b` | 69.38% | 42.60% | 35.00% |
| `mistral-small3.2:latest` | 66.09% | 34.78% | 34.62% |
| `gemma3:12b` | 66.40% | 32.95% | 33.37% |
| `gemma3:4b` | 36.01% | 23.79% | 22.21% |

**Text only → visual, within the same course**, as text-only accuracy → visual accuracy (difference in points). Headers give the text-only / visual question counts. Only courses with at least 40 questions of each type are shown.

| Model | FEN (135 / 182) | FİZİK (43 / 181) | BİYOLOJİ (139 / 66) | COĞRAFYA (278 / 118) |
|---|---|---|---|---|
| `gemma4:31b` | 97.78% → 78.02% (−19.76) | 88.37% → 71.27% (−17.10) | 98.56% → 86.36% (−12.20) | 95.32% → 68.64% (−26.68) |
| `muse-glimmer:30b` | 98.52% → 83.52% (−15.00) | 83.72% → 83.98% (+0.26) | 95.68% → 92.42% (−3.26) | 90.29% → 72.88% (−17.41) |
| `qwen3.8:27b` | 98.52% → 89.01% (−9.51) | 88.37% → 83.98% (−4.39) | 96.40% → 93.94% (−2.46) | 93.53% → 70.34% (−23.19) |
| `ornith-1.5:35b` | 94.81% → 80.22% (−14.60) | 86.05% → 76.24% (−9.80) | 96.40% → 86.36% (−10.04) | 87.05% → 71.19% (−15.86) |
| `gemma4:e4b` | 86.67% → 54.95% (−31.72) | 76.74% → 45.86% (−30.89) | 89.21% → 62.12% (−27.09) | 81.29% → 48.31% (−32.99) |
| `gemma3:27b` | 71.85% → 35.71% (−36.14) | 58.14% → 32.60% (−25.54) | 82.73% → 48.48% (−34.25) | 74.46% → 43.22% (−31.24) |
| `ministral-3:14b` | 69.63% → 39.01% (−30.62) | 51.16% → 35.36% (−15.80) | 78.42% → 46.97% (−31.45) | 75.18% → 39.83% (−35.35) |
| `mistral-small3.2:latest` | 69.63% → 37.36% (−32.27) | 53.49% → 30.39% (−23.10) | 69.06% → 43.94% (−25.13) | 73.74% → 41.53% (−32.22) |
| `gemma3:12b` | 65.93% → 39.56% (−26.37) | 55.81% → 27.07% (−28.74) | 69.78% → 39.39% (−30.39) | 69.78% → 42.37% (−27.41) |
| `gemma3:4b` | 34.81% → 21.43% (−13.39) | 41.86% → 24.31% (−17.55) | 31.65% → 16.67% (−14.99) | 35.61% → 22.88% (−12.73) |

**MATEMATİK by question type**, the course with the most expression questions. Its 54 text-only questions make that column less precise.

| Model | Text only (54) | Expression (687) | Visual (158) |
|---|---:|---:|---:|
| `gemma4:31b` | 100.00% | 99.13% | 84.81% |
| `muse-glimmer:30b` | 100.00% | 99.27% | 93.67% |
| `qwen3.8:27b` | 98.15% | 98.69% | 94.30% |
| `ornith-1.5:35b` | 96.30% | 99.42% | 87.34% |
| `gemma4:e4b` | 94.44% | 95.92% | 56.96% |
| `gemma3:27b` | 22.22% | 30.42% | 28.48% |
| `ministral-3:14b` | 33.33% | 34.64% | 27.85% |
| `mistral-small3.2:latest` | 24.07% | 25.47% | 32.28% |
| `gemma3:12b` | 25.93% | 25.47% | 27.22% |
| `gemma3:4b` | 27.78% | 22.56% | 18.35% |

### 7.3 Efficiency

| Model | Median (s) | Mean (s) | 95th percentile (s) | Total (hours) |
|---|---:|---:|---:|---:|
| `gemma4:31b` | 9.66 | 24.22 | 65.3 | 32.7 |
| `muse-glimmer:30b` | 9.44 | 18.86 | 63.1 | 25.5 |
| `qwen3.8:27b` | 4.55 | 7.49 | 20.5 | 10.1 |
| `ornith-1.5:35b` | 1.74 | 11.86 | 125.2 | 16.0 |
| `gemma4:e4b` | 3.78 | 5.14 | 13.3 | 6.9 |
| `gemma3:27b` | 0.58 | 0.63 | 0.9 | 0.8 |
| `ministral-3:14b` | 0.23 | 0.24 | 0.3 | 0.3 |
| `mistral-small3.2:latest` | 0.37 | 0.39 | 0.5 | 0.5 |
| `gemma3:12b` | 0.32 | 0.39 | 0.6 | 0.5 |
| `gemma3:4b` | 0.16 | 0.22 | 0.3 | 0.3 |

## 8. Failures

Every invalid answer was output that couldn't be parsed as the expected JSON.

| Model | Invalid | Share | Duration of failed requests |
|---|---:|---:|---|
| `ornith-1.5:35b` | 324 | 6.67% | 123–129 s |
| `gemma4:31b` | 77 | 1.59% | 525–563 s |
| `qwen3.8:27b` | 16 | 0.33% | 12–238 s |
| `muse-glimmer:30b` | 14 | 0.29% | 435–441 s |
| `gemma4:e4b` | 1 | 0.02% | 9 s |
| Other five models | 0 | 0.00% | |

- **Likely cause for three models:** for `ornith-1.5:35b`, `gemma4:31b` and `muse-glimmer:30b`, failed requests ended after a nearly fixed time. This is consistent with output reaching the context limit and being cut off.
- **Unknown cause for two models:** the failures of `qwen3.8:27b` and `gemma4:e4b` vary in duration. Raw outputs aren't saved, so their cause can't be confirmed.
- **Not counted as failures:** ID mismatches, where the returned ID doesn't match the question. `mistral-small3.2:latest` returned "Soru ID: 1" instead of "1" for 4,712 answers, and `gemma4:e4b` did the same for 115.

## 9. Analysis

- **The top three are close.** `gemma4:31b` leads `muse-glimmer:30b` by 1.28 points and `qwen3.8:27b` by 1.46 points (section 7.1).
- **Thinking support goes with higher accuracy.** All five thinking-capable models outscore all five others (sections 5 and 7.1). This doesn't show that thinking causes the gap:
  - the two groups also differ in model family and size
  - thinking wasn't set, and raw outputs weren't saved, so whether each model actually thought isn't confirmed. Response times suggest they did (section 7.3).
- **Size isn't decisive across families.** `gemma4:e4b` (8.0B) scores 75.36%, above every model without thinking support, including models of 12.2–27.4B (section 7.1).
- **Size helps within a family.** In the `gemma3` family, accuracy rises with size: 30.03% at 4.3B, 51.05% at 12.2B and 56.75% at 27.4B (section 7.1).
- **Visuals cost accuracy for every model.** Within FEN, BİYOLOJİ and COĞRAFYA, all ten models score lower on visual questions than on text-only ones, and in FİZİK all but `muse-glimmer:30b`. COĞRAFYA visuals are hard even for the strongest models: they drop 15.86–26.68 points. `gemma4:e4b` drops 27–33 points in every course, more than the other thinking-capable models (section 7.2).
- **Rendering expressions as images costs little.** In MATEMATİK, each model scores about the same on expression questions as on text-only ones (section 7.2).
- **Models without thinking support are weak at maths whatever the format.** In MATEMATİK they score 22–35% on text-only, expression and visual questions alike, close to the 20% of random guessing. Their low overall score on expression questions therefore reflects the subject, not reading images (section 7.2).
- **GEOMETRİ is near chance for models without thinking support.** They score 21.72–28.62% on GEOMETRİ, where 99% of questions include an image. GEOMETRİ has too few text-only questions to separate the subject from the images (section 7.2).
- **EDEBİYAT is hard even for strong models.** It's the weakest course for `muse-glimmer:30b` (78.48%), `qwen3.8:27b` (76.19%) and `ornith-1.5:35b` (66.67%). `gemma4:31b`'s weakest course is FİZİK (79.72%) (section 7.2).
- **Invalid answers cost `ornith-1.5:35b` most.** Its 324 invalid answers drop it to fourth place. Among valid answers it scores 92.70%, second only to `gemma4:31b`. 124 of these failures fall in EDEBİYAT and TÜRKÇE (sections 7.1 and 8).
- **Speed varies by up to 60 times.** `gemma4:31b` and `muse-glimmer:30b` take about 9.5 seconds per question at the median, against 0.16–0.58 seconds for models without thinking support (section 7.3).

## 10. Limitations

- **One prompt setup:**
  - All results use prompt setup v1, and how much the setup affects scores hasn't been tested.
  - Thinking wasn't controlled, so thinking-capable models may have reasoned at length despite the prompt asking for no explanation. Their times suggest they did.
- **Thinking isn't isolated:** no model was run both with and without thinking, so the benefit of thinking itself isn't measured. Running the same models, such as `qwen3.8:27b` and `gemma4:e4b`, with thinking on and off would separate the effect of thinking from the model. That would be a new run with its own settings version.
- **Context limit:** the observed limit of 32,768 tokens likely caused most invalid answers. A different limit could change invalid counts and accuracy for thinking-capable models.
- **No raw outputs:** only parsed answers are saved, so failure causes can't be confirmed and no example answers can be shown.
- **Timing:**
  - All times were measured on one machine and depend on its hardware.
  - The Ollama version was recorded only at the time of writing.
- **Single run:** each model was run once, at temperature 0.
- **Not measured:** calibration, meaning whether a model knows when it's unsure, and robustness, meaning whether answers hold when a question is slightly reworded.
- **Visual questions may be harder in themselves:** within a course, visual questions may cover different topics or need more steps than text-only ones, so the visual gap isn't only about reading images. This hasn't been measured.
- **Data issues:** course and image use are tangled, and questions may appear in training data (section 3).

## 11. Reproducibility

- **Command:** run this from the repository root:
  ```
  uv run src/tr_ai_evals/benchmarks/university_entrance/run_all_models.py
  ```
- **Settings:** the constants at the top of `run_all_models.py`, with `RETRY_FAILED = False`.
- **Run outputs:** `experiments/experiment_1/<run id>/`, kept locally and not in the repository. Run IDs:
  - `gemma4-31b_91c4e54d`
  - `muse-glimmer-30b_750f056b`
  - `qwen3.8-27b_de705885`
  - `ornith-1.5-35b_a333b496`
  - `gemma4-e4b_001acb8d`
  - `gemma3-27b_56419342`
  - `ministral-3-14b_edbbf95e`
  - `mistral-small3.2-latest_fee57121`
  - `gemma3-12b_d3ecdaae`
  - `gemma3-4b_24288be1`
- **Tables:** computed from the first record for each question in each run's `answers.jsonl`, joined with dataset `v1` for course and image information. The `gemma4:31b` file also holds 80 later records for 76 of its questions, left by an earlier version of the code; they aren't scored. A script to regenerate them isn't in the repository yet.

## 12. Version history

| Date | Change |
|---|---|
| 2026-11-16 | First version |
| 2026-11-17 | Clarified that the thinking comparison shows a link, not a cause, and added it as a limitation |
| 2026-11-17 | Split image questions into expression and visual questions, and compared them with text-only questions within courses |
| 2026-11-17 | Scored `gemma4:31b` on its first attempts, so every model has one attempt per question |
| 2026-11-17 | Narrowed the intended use to Turkish academic question answering, and widened the out-of-scope list |
