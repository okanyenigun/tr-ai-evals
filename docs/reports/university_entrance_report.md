# Turkish University Entrance Exam Benchmark: Report

**Date:** 2026-11-16

## 1. Summary

Ten models, all run locally, answered all 4,858 questions from Turkish university entrance exams held in 2006–2017.

- **Top three:** `gemma4:31b` scored highest at 92.71%, ahead of `muse-glimmer:30b` (90.90%) and `qwen3.8:27b` (90.72%).
- **Thinking support:** the five models that support thinking all scored above 75%, and the five that don't all scored below 57%.
- **Speed:** the thinking-capable models took 2–10 seconds per question at the median, against under 1 second for the others.
- **Image questions:** models without thinking support scored up to 37 points lower on questions with an image than on text-only ones.
- **Main caveats:** all results come from one prompt setup that doesn't control thinking. Image questions are mostly maths and science, so the image gap also reflects subject.

## 2. Benchmark

- **Purpose:** Turkish academic knowledge and reasoning, measured with real exam questions
- **Task:** choose the one correct option (A–E) for a multiple-choice question, some with an image
- **Domain and language:** national university entrance exams (ÖSS, YGS, LYS) across 12 course labels, 2006–2017, in Turkish
- **Intended use:** helping people choose a model for Turkish-language work
- **Out of scope:**
  - everyday Turkish use, such as writing or summarizing
  - comparison with human candidates' exam scores

## 3. Data

- **Source:** ÖSYM exam papers, via [`yeniguno/turkish-university-entrance-exam-questions`](https://huggingface.co/datasets/yeniguno/turkish-university-entrance-exam-questions)
- **Version:** `v1`, revision `078b264`
- **Size:** 4,858 questions from 118 exam papers, in one split, all used
- **Composition:**
  - 12 course labels, with question counts shown in section 7.2
  - by exam: ÖSS 2006–2009 (923 questions), YGS 2010–2017 (1,291) and LYS 2010–2017 (2,644)
  - 2,616 text-only questions and 2,242 with an image: 1,040 with a visual, and 1,202 with a cropped booklet image because they contain an expression
  - a balanced answer key, with 958–994 questions per letter
- **Known issues:**
  - **Course and image use are tangled.** 85–99% of GEOMETRİ, MATEMATİK, KİMYA and FİZİK questions include an image, against 2% for EDEBİYAT, TARİH and TÜRKÇE. A course score therefore reflects both subject knowledge and the ability to read images.
  - **Questions may be in training data.** All questions come from public exams held in 2006–2017, so models may have seen them during training. Scores may partly reflect memorized questions rather than reasoning, and this hasn't been measured.

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

- **Invalid outputs:** an answer that can't be parsed counts as wrong and isn't asked again. `gemma4:31b` is the exception (see section 10).
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
| `gemma4:31b` | 92.71% | 99.28% | 93.39% |
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
| `gemma4:31b` | 95.45% | 88.43% | 88.00% | 96.25% | 90.00% | 82.52% | 91.03% | 96.69% | 97.00% | 93.78% | 95.64% | 93.35% |
| `muse-glimmer:30b` | 94.63% | 85.54% | 78.48% | 91.42% | 91.67% | 86.01% | 95.86% | 96.69% | 98.33% | 89.63% | 91.94% | 88.30% |
| `qwen3.8:27b` | 95.45% | 86.99% | 76.19% | 94.10% | 94.52% | 87.06% | 94.48% | 96.32% | 97.89% | 91.29% | 89.76% | 84.86% |
| `ornith-1.5:35b` | 93.80% | 82.89% | 66.67% | 90.35% | 89.05% | 82.17% | 90.34% | 95.22% | 97.11% | 87.14% | 86.06% | 77.29% |
| `gemma4:e4b` | 79.75% | 72.29% | 60.95% | 80.97% | 73.10% | 59.09% | 66.55% | 84.93% | 88.99% | 76.35% | 73.86% | 74.08% |
| `gemma3:27b` | 71.07% | 64.82% | 66.48% | 78.82% | 52.62% | 37.41% | 28.62% | 51.10% | 29.59% | 75.93% | 80.39% | 69.95% |
| `ministral-3:14b` | 66.53% | 64.58% | 54.48% | 76.68% | 53.57% | 40.91% | 26.90% | 55.15% | 33.37% | 74.69% | 77.78% | 64.91% |
| `mistral-small3.2:latest` | 59.92% | 63.86% | 51.05% | 75.34% | 51.43% | 36.36% | 25.17% | 55.51% | 26.59% | 70.54% | 73.42% | 59.17% |
| `gemma3:12b` | 59.50% | 60.72% | 55.62% | 73.99% | 49.05% | 33.92% | 27.59% | 43.75% | 25.81% | 69.29% | 74.51% | 62.61% |
| `gemma3:4b` | 26.45% | 31.81% | 27.43% | 44.24% | 26.90% | 26.92% | 21.72% | 28.68% | 22.14% | 44.40% | 37.91% | 32.80% |

**Accuracy by question type:**

| Model | Text only (2,616) | With image (2,242) | Difference |
|---|---:|---:|---:|
| `gemma4:31b` | 94.00% | 91.21% | −2.79 |
| `muse-glimmer:30b` | 89.11% | 93.00% | +3.89 |
| `qwen3.8:27b` | 88.57% | 93.22% | +4.65 |
| `ornith-1.5:35b` | 83.14% | 90.45% | +7.31 |
| `gemma4:e4b` | 76.11% | 74.49% | −1.62 |
| `gemma3:27b` | 73.85% | 36.80% | −37.05 |
| `ministral-3:14b` | 69.38% | 39.07% | −30.31 |
| `mistral-small3.2:latest` | 66.09% | 34.70% | −31.39 |
| `gemma3:12b` | 66.40% | 33.14% | −33.26 |
| `gemma3:4b` | 36.01% | 23.06% | −12.95 |

### 7.3 Efficiency

Per-question times use each question's scored attempt. Total time includes every attempt.

| Model | Median (s) | Mean (s) | 95th percentile (s) | Total (hours) |
|---|---:|---:|---:|---:|
| `gemma4:31b` | 9.66 | 20.63 | 60.4 | 39.6 |
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
| `gemma4:31b` | 35 | 0.72% | 526–530 s |
| `qwen3.8:27b` | 16 | 0.33% | 12–238 s |
| `muse-glimmer:30b` | 14 | 0.29% | 435–441 s |
| `gemma4:e4b` | 1 | 0.02% | 9 s |
| Other five models | 0 | 0.00% | |

- **Likely cause for three models:** for `ornith-1.5:35b`, `gemma4:31b` and `muse-glimmer:30b`, failed requests ended after a nearly fixed time. This is consistent with output reaching the context limit and being cut off.
- **Unknown cause for two models:** the failures of `qwen3.8:27b` and `gemma4:e4b` vary in duration. Raw outputs aren't saved, so their cause can't be confirmed.
- **Not counted as failures:** ID mismatches, where the returned ID doesn't match the question. `mistral-small3.2:latest` returned "Soru ID: 1" instead of "1" for 4,712 answers, and `gemma4:e4b` did the same for 115.

## 9. Analysis

- **The top three are close.** `gemma4:31b` leads `muse-glimmer:30b` by 1.81 points and `qwen3.8:27b` by 1.99 points (section 7.1).
- **Thinking support divides the results.** All five thinking-capable models outscore all five others (sections 5 and 7.1). These models also differ in family and size, so thinking can't be credited alone.
- **Size isn't decisive across families.** `gemma4:e4b` (8.0B) scores 75.36%, above every model without thinking support, including models of 12.2–27.4B (section 7.1).
- **Size helps within a family.** In the `gemma3` family, accuracy rises with size: 30.03% at 4.3B, 51.05% at 12.2B and 56.75% at 27.4B (section 7.1).
- **Image questions split the models.** The five models without thinking support score 13–37 points lower on image questions. Thinking-capable models score within 3 points either way, or higher (section 7.2).
- **GEOMETRİ is near chance without thinking.** The five models without thinking support score 21.72–28.62% on GEOMETRİ, where 99% of questions include an image (section 7.2).
- **EDEBİYAT is hard even for strong models.** It's the weakest course for `muse-glimmer:30b` (78.48%), `qwen3.8:27b` (76.19%) and `ornith-1.5:35b` (66.67%). `gemma4:31b`'s weakest course is FİZİK (82.52%) (section 7.2).
- **Invalid answers cost `ornith-1.5:35b` most.** Its 324 invalid answers drop it to fourth place. Among valid answers it scores 92.70%, second only to `gemma4:31b`. 124 of these failures fall in EDEBİYAT and TÜRKÇE (sections 7.1 and 8).
- **Speed varies by up to 60 times.** `gemma4:31b` and `muse-glimmer:30b` take about 9.5 seconds per question at the median, against 0.16–0.58 seconds for models without thinking support (section 7.3).

## 10. Limitations

- **One prompt setup:**
  - All results use prompt setup v1, and how much the setup affects scores hasn't been tested.
  - Thinking wasn't controlled, so thinking-capable models may have reasoned at length despite the prompt asking for no explanation. Their times suggest they did.
- **Unequal retries:** before the retry policy changed, `gemma4:31b` got a second attempt on 76 failed questions, and 42 of them became valid answers. On first attempts alone its accuracy is 92.18%, which still ranks first. No other model was retried.
- **Context limit:** the observed limit of 32,768 tokens likely caused most invalid answers. A different limit could change invalid counts and accuracy for thinking-capable models.
- **No raw outputs:** only parsed answers are saved, so failure causes can't be confirmed and no example answers can be shown.
- **Timing:**
  - All times were measured on one machine and depend on its hardware.
  - The Ollama version was recorded only at the time of writing.
- **Single run:** each model was run once, at temperature 0.
- **Not measured:** calibration, meaning whether a model knows when it's unsure, and robustness, meaning whether answers hold when a question is slightly reworded.
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
- **Tables:** computed from the latest attempt per question in each run's `answers.jsonl`, joined with dataset `v1` for course and image information. A script to regenerate them isn't in the repository yet.

## 12. Version history

| Date | Change |
|---|---|
| 2026-11-16 | First version |
