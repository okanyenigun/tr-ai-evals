# MMLU-TR Benchmark: Report

**Date:** 2026-11-17

## 1. Summary

Ten models, all run locally, answered all 14,042 test questions of MMLU-TR, a Turkish machine translation of the MMLU knowledge benchmark. Five of them also answered the original English questions, for comparison.

- **Top two:** `mistral-small3.2:latest` (70.84%) and `ministral-3:14b` (70.81%) are tied, 4 questions apart, and about 10 points ahead of `gemma4:e4b` (60.79%).
- **Turkish costs accuracy:** the five models run in both languages all score lower in Turkish, by 8.00 to 19.53 points. Their order also changes, so an English ranking doesn't predict the Turkish one.
- **Answer format:** `qwen3.8:27b` and `gemma4:12b-it-q8_0` often didn't answer with a letter (34.34% and 14.04% of questions), so their accuracy understates what they know.

## 2. Benchmark

- **Purpose:** broad academic and professional knowledge in Turkish, and how much of a model's English performance carries over to Turkish
- **Task:** choose the one correct option (A–D) for a multiple-choice question, after five solved examples from the same subject, and answer with a single letter
- **Domain and language:** 57 subjects, from elementary mathematics to professional law and medicine, at high school, university and professional level. Questions are machine-translated from English into Turkish. The English originals serve as the baseline.
- **Intended use:**
  - comparing models on Turkish academic and professional knowledge questions, as one input when choosing a model for Turkish-language work
  - showing how far English benchmark scores overstate a model's performance in Turkish
- **Out of scope:**
  - knowledge about Turkey: the questions were translated, not adapted, and include US law, US history and US moral standards
  - general Turkish proficiency, such as conversation, following instructions, writing, summarizing or understanding documents
  - comparison with MMLU scores published elsewhere, which use other prompts, settings and model versions

## 3. Data

- **Source:**
  - **English:** MMLU (Hendrycks et al., 2021), MIT licence, via [`cais/mmlu`](https://huggingface.co/datasets/cais/mmlu), config `all`
  - **Turkish:** [`yeniguno/mmlu-tr`](https://huggingface.co/datasets/yeniguno/mmlu-tr), MIT licence, a machine translation of MMLU
- **Version:**
  - Turkish: `mmlu_tr_questions` v1, revision `d2c8c04`
  - English: `mmlu_en_questions` v1, revision `c30699e`
- **Size:** both datasets have the same three splits, aligned row by row, so each Turkish question has the same ID as its English original:
  - test, 14,042 questions: all scored
  - dev, 285 questions: the five solved examples per subject
  - validation, 1,531 questions: not used
- **Composition:**
  - 57 subjects with 100–1,534 questions each. `professional_law` alone has 1,534 (10.92%) and `moral_scenarios` 895 (6.37%).
  - four categories, as grouped by the MMLU authors: Humanities (13 subjects, 4,705 questions), Other (14, 3,242), Social sciences (12, 3,077) and STEM (18, 3,018). Appendix B lists the subjects in each.
  - a near-balanced answer key: A 22.95%, B 24.65%, C 25.51%, D 26.89%

## 4. Evaluation method

- **Prompting:** five-shot, with the same prompt for every model and no tuning for any of them. The format and the choice of examples follow Stanford HELM's MMLU evaluation. In three subjects checked against HELM's published prompts, the English prompts match them character for character. Each prompt has:
  - **Header:** one line naming the subject. In Turkish (template v1, with Turkish subject names): "Aşağıdakiler {subject} hakkında çoktan seçmeli sorulardır (cevaplarıyla birlikte)." In English (template v1): "The following are multiple choice questions (with answers) about {subject}."
  - **Examples:** five solved questions from the subject's dev split, each with "Soru:" or "Question:", options A–D, and "Cevap: X" or "Answer: X". Both languages use the same five questions in the same order, chosen with a fixed random seed (0) so that their correct answers vary.
  - **Test question:** in the same form, ending with "Cevap:" or "Answer:" for the model to complete
  - **Delivery:** the prompt is sent as plain text, without the model's chat template, so the model continues the text. Appendix A shows a full example.
- **Generation settings** (params v1, the same in both languages):
  - temperature 0
  - one output token, which leaves no room for thinking
  - context length 8,192 tokens. The longest prompt was 4,802 tokens, so no prompt was cut.
- **Output format:** a single letter. The generated token, with surrounding spaces removed, must be exactly A, B, C or D.
- **Scoring:** the letter is compared with the answer key.
- **Metrics:**

| Metric | Definition | Direction |
|---|---|---|
| **Accuracy** (primary) | Correct answers ÷ all 14,042 questions | Higher is better |
| **Valid-answer rate** | Questions answered with a letter A–D ÷ all questions | Higher is better |
| **Accuracy among valid answers** | Correct answers ÷ valid answers | Higher is better |
| **Turkish–English gap** | Turkish accuracy − English accuracy, in points | Closer to zero is better |
| **Time per question** | Wall-clock seconds per request | Lower is better |

- **Invalid outputs:** anything other than a single letter counts as wrong and isn't asked again. No request failed with an error.
- **Baselines:**
  - random guessing: 25.00%
  - always choosing the most common letter (D): 26.89%
  - the English results of the five models run in both languages (section 7.1)

## 5. Models

All models were run through Ollama. Several also accept images or audio, but only text was used.

| Model | Version (digest) | Size | Quantization | Access | Modality | Languages | Notes |
|---|---|---|---|---|---|---|---|
| `mistral-small3.2:latest` | `5a408ab55df5` | 24.0B | Q4_K_M | Open weights | Text, image | Turkish | |
| `ministral-3:14b` | `4760c35aeb9d` | 13.9B | Q4_K_M | Open weights | Text, image | Turkish | |
| `gemma4:e4b` | `c6eb396dbd59` | 8.0B | Q4_K_M | Open weights | Text, image, audio | Turkish | Supports thinking |
| `qwen2.5:7b` | `845dbda0ea48` | 7.6B | Q4_K_M | Open weights | Text | Turkish, English | |
| `qwen3.8:27b` | `aaee06c39dcf` | 27.3B | Q4_K_M | Open weights | Text, image | Turkish | Supports thinking |
| `gemma3:4b` | `a2af6cc3eb7f` | 4.3B | Q4_K_M | Open weights | Text, image | Turkish, English | |
| `qwen3.5:2b` | `0689d44085e0` | 1.9B | Q8_0 | Open weights | Text, image | Turkish, English | Supports thinking |
| `qwen2.5:3b` | `357c53fb659c` | 3.1B | Q4_K_M | Open weights | Text | Turkish, English | |
| `gemma4:12b-it-q8_0` | `41c402fdddc2` | 11.9B | Q8_0 | Open weights | Text, image, audio | Turkish | Supports thinking |
| `gemma2:2b` | `8ccf136fdd52` | 2.6B | Q4_0 | Open weights | Text | Turkish, English | |

## 6. Run environment

- **Run date:** 2026-11-17, for both languages
- **Hardware:** NVIDIA GeForce RTX 5090 (32 GB), AMD Ryzen 7 9800X3D, 46 GiB RAM, Ubuntu 24.04.5
- **Software:** Ollama 0.34.2, Python 3.12.3, `ollama` 0.6.3, `datasets` 5.1.0
- **Code version:** the commit that adds this report, on top of `03e7f87`

## 7. Results

### 7.1 Overall

**Turkish:**

| Model | Accuracy | Valid-answer rate | Accuracy among valid answers |
|---|---:|---:|---:|
| `mistral-small3.2:latest` | 70.84% | 100.00% | 70.84% |
| `ministral-3:14b` | 70.81% | 100.00% | 70.81% |
| `gemma4:e4b` | 60.79% | 99.96% | 60.81% |
| `qwen2.5:7b` | 57.67% | 99.99% | 57.67% |
| `qwen3.8:27b` | 52.85% | 65.66% | 80.49% |
| `gemma3:4b` | 49.69% | 99.99% | 49.69% |
| `qwen3.5:2b` | 48.23% | 100.00% | 48.23% |
| `qwen2.5:3b` | 45.31% | 100.00% | 45.31% |
| `gemma4:12b-it-q8_0` | 45.17% | 85.96% | 52.55% |
| `gemma2:2b` | 43.63% | 100.00% | 43.63% |

**English and Turkish**, for the five models run in both. Valid-answer rates in English are 99.99–100.00%. Gaps are computed before rounding.

| Model | English accuracy | Turkish accuracy | Gap (points) |
|---|---:|---:|---:|
| `qwen2.5:7b` | 73.24% | 57.67% | −15.57 |
| `gemma3:4b` | 57.68% | 49.69% | −8.00 |
| `qwen3.5:2b` | 61.89% | 48.23% | −13.65 |
| `qwen2.5:3b` | 64.84% | 45.31% | −19.53 |
| `gemma2:2b` | 56.02% | 43.63% | −12.39 |

**Question by question**, as a share of the 14,042 questions:

| Model | Right in both | English only | Turkish only | Neither | Same letter in both |
|---|---:|---:|---:|---:|---:|
| `qwen2.5:7b` | 51.02% | 22.23% | 6.65% | 20.10% | 63.76% |
| `gemma3:4b` | 40.84% | 16.84% | 8.84% | 33.47% | 63.58% |
| `qwen3.5:2b` | 39.30% | 22.59% | 8.94% | 29.18% | 56.22% |
| `qwen2.5:3b` | 37.40% | 27.44% | 7.90% | 27.25% | 52.75% |
| `gemma2:2b` | 34.50% | 21.51% | 9.12% | 34.86% | 57.27% |

### 7.2 By category

**Turkish accuracy by category**, with question counts in the headers:

| Model | STEM (3,018) | Humanities (4,705) | Social sciences (3,077) | Other (3,242) |
|---|---:|---:|---:|---:|
| `mistral-small3.2:latest` | 69.28% | 64.29% | 77.93% | 75.05% |
| `ministral-3:14b` | 71.11% | 62.21% | 78.68% | 75.54% |
| `gemma4:e4b` | 59.15% | 53.39% | 69.68% | 64.62% |
| `qwen2.5:7b` | 57.49% | 50.05% | 64.38% | 62.52% |
| `qwen3.8:27b` | 55.50% | 37.30% | 74.52% | 52.38% |
| `gemma3:4b` | 45.06% | 45.63% | 55.80% | 54.07% |
| `qwen3.5:2b` | 46.98% | 43.08% | 54.24% | 51.17% |
| `qwen2.5:3b` | 43.67% | 41.23% | 49.07% | 49.17% |
| `gemma4:12b-it-q8_0` | 43.84% | 39.53% | 49.01% | 50.96% |
| `gemma2:2b` | 38.34% | 41.59% | 47.71% | 47.62% |

**English to Turkish by category**, as English accuracy → Turkish accuracy (gap in points):

| Model | STEM | Humanities | Social sciences | Other |
|---|---|---|---|---|
| `qwen2.5:7b` | 68.99% → 57.49% (−11.50) | 66.76% → 50.05% (−16.71) | 82.87% → 64.38% (−18.49) | 77.48% → 62.52% (−14.96) |
| `gemma3:4b` | 50.83% → 45.06% (−5.77) | 51.16% → 45.63% (−5.53) | 67.47% → 55.80% (−11.67) | 64.25% → 54.07% (−10.18) |
| `qwen3.5:2b` | 59.41% → 46.98% (−12.43) | 54.52% → 43.08% (−11.43) | 72.38% → 54.24% (−18.13) | 64.93% → 51.17% (−13.76) |
| `qwen2.5:3b` | 59.94% → 43.67% (−16.27) | 57.81% → 41.23% (−16.58) | 76.24% → 49.07% (−27.17) | 68.78% → 49.17% (−19.62) |
| `gemma2:2b` | 48.11% → 38.34% (−9.77) | 49.59% → 41.59% (−7.99) | 67.24% → 47.71% (−19.53) | 62.06% → 47.62% (−14.44) |

**Subjects with the largest and smallest gaps**, averaged over the five models. Appendix D lists all 57.

| Subject | Category | Questions | English | Turkish | Gap (points) |
|---|---|---:|---:|---:|---:|
| high_school_government_and_politics | Social sciences | 193 | 84.25% | 57.31% | −26.94 |
| college_biology | STEM | 144 | 74.17% | 48.89% | −25.28 |
| high_school_psychology | Social sciences | 545 | 83.19% | 59.60% | −23.60 |
| high_school_microeconomics | Social sciences | 238 | 73.45% | 53.11% | −20.34 |
| logical_fallacies | Humanities | 163 | 75.83% | 55.58% | −20.25 |
| … | | | | | |
| elementary_mathematics | STEM | 378 | 53.44% | 46.83% | −6.61 |
| high_school_mathematics | STEM | 270 | 41.19% | 34.96% | −6.22 |
| formal_logic | Humanities | 126 | 46.35% | 43.65% | −2.70 |
| college_mathematics | STEM | 100 | 36.00% | 34.40% | −1.60 |
| global_facts | Other | 100 | 33.60% | 34.00% | +0.40 |

Appendix C gives Turkish accuracy by subject for all ten models.

### 7.3 Efficiency

Each answer is a single token, so time per question is mostly time spent reading the prompt.

**Turkish:**

| Model | Median (s) | Mean (s) | 95th percentile (s) | Total (minutes) | Mean prompt (tokens) |
|---|---:|---:|---:|---:|---:|
| `mistral-small3.2:latest` | 0.033 | 0.045 | 0.109 | 10.5 | 1,062 |
| `ministral-3:14b` | 0.024 | 0.031 | 0.070 | 7.2 | 1,060 |
| `gemma4:e4b` | 0.035 | 0.037 | 0.055 | 8.6 | 971 |
| `qwen2.5:7b` | 0.016 | 0.020 | 0.045 | 4.6 | 1,108 |
| `qwen3.8:27b` | 0.270 | 0.272 | 0.360 | 63.7 | 1,012 |
| `gemma3:4b` | 0.045 | 0.051 | 0.090 | 12.0 | 970 |
| `qwen3.5:2b` | 0.029 | 0.029 | 0.038 | 6.9 | 1,012 |
| `qwen2.5:3b` | 0.013 | 0.016 | 0.031 | 3.7 | 1,108 |
| `gemma4:12b-it-q8_0` | 0.112 | 0.126 | 0.226 | 29.6 | 971 |
| `gemma2:2b` | 0.028 | 0.036 | 0.083 | 8.5 | 983 |

**English:**

| Model | Median (s) | Mean (s) | 95th percentile (s) | Total (minutes) | Mean prompt (tokens) |
|---|---:|---:|---:|---:|---:|
| `qwen2.5:7b` | 0.013 | 0.015 | 0.031 | 3.6 | 708 |
| `gemma3:4b` | 0.038 | 0.044 | 0.083 | 10.3 | 718 |
| `qwen3.5:2b` | 0.025 | 0.026 | 0.036 | 6.0 | 723 |
| `qwen2.5:3b` | 0.011 | 0.013 | 0.024 | 3.0 | 708 |
| `gemma2:2b` | 0.023 | 0.029 | 0.060 | 6.8 | 718 |

## 8. Failures

No request failed with an error. Every invalid answer is a first token that isn't a letter.

## 9. Analysis

- **The top two are tied.** `mistral-small3.2:latest` (9,947 correct) leads `ministral-3:14b` (9,943) by 4 questions. Both are about 10 points ahead of `gemma4:e4b` (section 7.1).
- **Every model loses accuracy in Turkish.** The five models run in both languages score 8.00–19.53 points lower in Turkish (section 7.1).
- **English rankings don't carry over.** `qwen2.5:3b` ranks second of the five in English and fourth in Turkish, with the largest loss (−19.53). `gemma3:4b` ranks fourth in English and second in Turkish, with the smallest loss (−8.00) (section 7.1).
- **Language changes individual answers, not just the total.** Only 52.75–63.76% of questions get the same letter in both languages, and 6.65–9.12% are answered correctly only in Turkish (section 7.1).
- **Social sciences lose the most.** It's the category with the largest drop for all five models, 11.67–27.17 points (section 7.2). The largest subject drops are in `high_school_government_and_politics` (−26.94), `college_biology` (−25.28) and `high_school_psychology` (−23.60).
- **Maths and logic lose the least, but from a low start.** `global_facts`, `college_mathematics` and `formal_logic` change by less than 3 points. In English, the five models already score only 33.60–46.35% on them, close to chance (section 7.2).
- **Accuracy mostly rises with size.** Among the eight models with at least 99.9% valid answers, it rises from 43.63% at 2.6B to about 70.8% at 13.9–24.0B. `qwen3.5:2b` (1.9B) is the exception: it scores 48.23%, ahead of two larger models (sections 5 and 7.1).
- **Answer format hides `qwen3.8:27b`'s knowledge.** It ranks fifth overall, but scores highest or tied highest in 29 of the 57 subjects, against near zero in subjects where it rarely answers with a letter, such as `professional_law` (1.11%) (appendix C).
- **`gemma4:12b-it-q8_0` trails the smaller `gemma4:e4b`.** Even among valid answers it scores 52.55%, against 60.81% for `gemma4:e4b` (section 7.1).
- **Turkish costs more tokens.** The same questions take 35–56% more prompt tokens in Turkish, and the Turkish runs took 14–29% longer (section 7.3).
- **Some questions defeat every model.** No model answered 672 questions (4.79%) correctly in Turkish, and all ten answered 980 (6.98%) correctly. Answer key and translation errors may account for some of the 672.

## 10. Limitations

- **One prompt format:**
  - All results use one plain-text, five-shot format with a one-letter answer. It suits models that answer directly, and penalizes models that open with a blank line, formatting or thinking: `qwen3.8:27b` and `gemma4:12b-it-q8_0`. A chat format or a longer answer limit could change their scores and the ranking.
  - How much the prompt wording or the choice of examples affects scores hasn't been tested.
- **Translation quality:** the translation wasn't fully reviewed by people, and at least one question has its meaning reversed. The Turkish–English gap therefore combines weaker Turkish with translation errors.
- **English baseline for five models only:** all five are small (1.9–7.6B), so the gap for larger models is unknown.
- **Training data overlap:** it may be larger for the English questions than for this translation, which would widen the measured gap. It hasn't been measured.
- **Mixed quantization:** most models use Q4_K_M, but `gemma2:2b` uses Q4_0, and `qwen3.5:2b` and `gemma4:12b-it-q8_0` use Q8_0. Quantization can affect accuracy.
- **Timing:** all times were measured on one machine and depend on its hardware.
- **Single run:** each model was run once, at temperature 0.
- **Not measured:** calibration, meaning whether a model knows when it's unsure, and robustness, meaning whether answers hold when a question is slightly reworded.
- **Data issues:** US-centred content and answer key errors.

## 11. Reproducibility

- **Commands:** run these from the repository root, the first for Turkish (experiment 1) and the second for English (experiment 2):
  ```
  uv run src/tr_ai_evals/benchmarks/mmlu_tr/run_all_models.py
  uv run src/tr_ai_evals/benchmarks/mmlu_tr/run_all_models_en.py
  ```
- **Settings:** the constants at the top of each script, with `RETRY_FAILED = False`. Each run records these versions in its manifest, with an 8-character hash of each file:

| Component | Turkish | English |
|---|---|---|
| Dataset | `mmlu_tr_questions` v1, revision `d2c8c04` | `mmlu_en_questions` v1, revision `c30699e` |
| Prompt template | `mmlu_tr_template` v1 (`54f2d89c`) | `mmlu_en_template` v1 (`c30fd524`) |
| Subject names | `mmlu_tr_subjects` v1 (`ec352b6a`) | `mmlu_en_subjects` v1 (`7408034f`) |
| Generation settings | `mmlu_tr_params` v1 (`e2bc6187`) | `mmlu_tr_params` v1 (`e2bc6187`) |
| Examples | 5 per subject (`ecf93939`) | 5 per subject (`ecf93939`) |

- **Run outputs:** `src/tr_ai_evals/benchmarks/mmlu_tr/experiments/experiment_<1 or 2>/<run id>/`, kept locally and not in the repository. Run IDs:
  - **Turkish:**
    - `mistral-small3.2-latest_f22d4602`
    - `ministral-3-14b_f0466772`
    - `gemma4-e4b_878f8826`
    - `qwen2.5-7b_46973d74`
    - `qwen3.8-27b_9b80669c`
    - `gemma3-4b_e5704934`
    - `qwen3.5-2b_fb1fa895`
    - `qwen2.5-3b_df74b8f9`
    - `gemma4-12b-it-q8-0_dd50ba46`
    - `gemma2-2b_4270c98c`
  - **English:**
    - `qwen2.5-7b_369c848e`
    - `gemma3-4b_9c4f1c11`
    - `qwen3.5-2b_90638954`
    - `qwen2.5-3b_0c9f42c5`
    - `gemma2-2b_34f744c0`
- **Tables:** computed from each run's `answers.jsonl`, which has one record per question. Categories follow the MMLU authors' grouping (appendix B). A script to regenerate them isn't in the repository yet.

## 12. Version history

| Date | Change |
|---|---|
| 2026-11-17 | First version |

## Appendix

### A. Example prompt

The shortest prompt in the benchmark, for `world_religions_test_0001`, exactly as sent. The model's answer is the token that follows the last line. The English text keeps MMLU's original spacing, including the double space after some "Question:" labels.

**Turkish:**

```
Aşağıdakiler dünya dinleri hakkında çoktan seçmeli sorulardır (cevaplarıyla birlikte).

Soru: Upanişadlar nasıl nitelendirilebilir?
A. Ritüel metinleri
B. Felsefi metinler
C. İlahiler
D. Köken anlatıları
Cevap: B

Soru: İmparatoru ve kami ile ilişkilerini temel alan bir tür ulusal kültü hangi Japon hükümeti teşvik etti?
A. Honen
B. Tanaka
C. Tokugawa
D. Meiji
Cevap: D

Soru: Yahudi erkekler için ahdin işareti nedir?
A. Gökkuşağı
B. Sünnet
C. Bir oğul
D. Bar mitzva
Cevap: B

Soru: “Göklerin Buyruğu”, yeni hükümdarları meşrulaştırmak amacıyla hangi hanedan döneminde geliştirildi?
A. Shang
B. Zhou
C. Han
D. Xia
Cevap: B

Soru: Budizm'deki İkinci Mücevher nedir?
A. Dharma
B. Sangha
C. Buda
D. Bodhisattva
Cevap: A

Soru: Murtiler ne olarak çevrilebilir?
A. Sunular
B. Dualar
C. Tezahürler
D. Putlar
Cevap:
```

**English:**

```
The following are multiple choice questions (with answers) about world religions.

Question: How can the Upanishads be characterized?
A. Ritual texts
B. Philosophical texts
C. Hymns
D. Origin stories
Answer: B

Question:  Which Japanese government promoted a kind of national cult based on the emperor and his associations with kami?
A. Honen
B. Tanaka
C. Tokugawa
D. Meiji
Answer: D

Question:  What is the sign of the covenant for Jewish males?
A. The rainbow
B. Circumcision
C. A son
D. Bar mitzvah
Answer: B

Question:  In which dynasty was the "Mandate of Heaven" developed to legitimatize the new rulers?
A. Shang
B. Zhou
C. Han
D. Xia
Answer: B

Question: What is the Second Gem in Buddhism?
A. The Dharma
B. The Sangha
C. The Buddha
D. The Bodhisattva
Answer: A

Question:  What can murtis be translated as?
A. Offerings
B. Prayers
C. Apparitions
D. Idols
Answer:
```

### B. Categories

- **STEM (18 subjects):** abstract_algebra, astronomy, college_biology, college_chemistry, college_computer_science, college_mathematics, college_physics, computer_security, conceptual_physics, electrical_engineering, elementary_mathematics, high_school_biology, high_school_chemistry, high_school_computer_science, high_school_mathematics, high_school_physics, high_school_statistics, machine_learning
- **Humanities (13):** formal_logic, high_school_european_history, high_school_us_history, high_school_world_history, international_law, jurisprudence, logical_fallacies, moral_disputes, moral_scenarios, philosophy, prehistory, professional_law, world_religions
- **Social sciences (12):** econometrics, high_school_geography, high_school_government_and_politics, high_school_macroeconomics, high_school_microeconomics, high_school_psychology, human_sexuality, professional_psychology, public_relations, security_studies, sociology, us_foreign_policy
- **Other (14):** anatomy, business_ethics, clinical_knowledge, college_medicine, global_facts, human_aging, management, marketing, medical_genetics, miscellaneous, nutrition, professional_accounting, professional_medicine, virology

### C. Turkish accuracy by subject

Subjects as rows and models as columns, with models in order of overall accuracy.

| Subject | Questions | `mistral-small3.2:latest` | `ministral-3:14b` | `gemma4:e4b` | `qwen2.5:7b` | `qwen3.8:27b` | `gemma3:4b` | `qwen3.5:2b` | `qwen2.5:3b` | `gemma4:12b-it-q8_0` | `gemma2:2b` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| abstract_algebra | 100 | 46.00% | 54.00% | 30.00% | 46.00% | 45.00% | 32.00% | 34.00% | 32.00% | 33.00% | 30.00% |
| anatomy | 135 | 69.63% | 71.85% | 58.52% | 50.37% | 78.52% | 45.93% | 45.93% | 38.52% | 65.93% | 37.04% |
| astronomy | 152 | 90.79% | 88.82% | 73.68% | 67.76% | 61.84% | 50.00% | 52.63% | 49.34% | 55.92% | 37.50% |
| business_ethics | 100 | 66.00% | 67.00% | 63.00% | 68.00% | 68.00% | 52.00% | 57.00% | 51.00% | 62.00% | 55.00% |
| clinical_knowledge | 265 | 82.26% | 78.49% | 70.19% | 65.28% | 88.68% | 55.09% | 57.74% | 52.08% | 73.58% | 45.66% |
| college_biology | 144 | 85.42% | 81.25% | 71.53% | 59.03% | 90.97% | 52.78% | 47.92% | 41.67% | 56.25% | 43.06% |
| college_chemistry | 100 | 49.00% | 54.00% | 42.00% | 46.00% | 60.00% | 39.00% | 38.00% | 30.00% | 39.00% | 32.00% |
| college_computer_science | 100 | 68.00% | 69.00% | 54.00% | 51.00% | 19.00% | 41.00% | 36.00% | 49.00% | 28.00% | 35.00% |
| college_mathematics | 100 | 48.00% | 52.00% | 43.00% | 36.00% | 12.00% | 35.00% | 34.00% | 34.00% | 30.00% | 33.00% |
| college_medicine | 173 | 79.19% | 77.46% | 60.69% | 60.12% | 63.01% | 47.98% | 50.87% | 45.66% | 38.73% | 42.77% |
| college_physics | 102 | 51.96% | 54.90% | 38.24% | 42.16% | 69.61% | 27.45% | 35.29% | 24.51% | 35.29% | 24.51% |
| computer_security | 100 | 78.00% | 79.00% | 74.00% | 72.00% | 84.00% | 66.00% | 56.00% | 61.00% | 65.00% | 57.00% |
| conceptual_physics | 235 | 78.72% | 80.43% | 69.36% | 62.98% | 91.49% | 49.36% | 51.49% | 43.40% | 61.28% | 36.60% |
| econometrics | 114 | 61.40% | 60.53% | 47.37% | 53.51% | 18.42% | 28.95% | 35.96% | 33.33% | 28.95% | 32.46% |
| electrical_engineering | 145 | 66.21% | 65.52% | 68.28% | 60.69% | 77.24% | 56.55% | 50.34% | 52.41% | 42.76% | 50.34% |
| elementary_mathematics | 378 | 71.43% | 76.19% | 58.20% | 63.76% | 15.34% | 40.48% | 43.12% | 47.35% | 49.74% | 39.42% |
| formal_logic | 126 | 61.11% | 62.70% | 50.00% | 52.38% | 11.11% | 43.65% | 49.21% | 43.65% | 34.13% | 29.37% |
| global_facts | 100 | 58.00% | 51.00% | 40.00% | 44.00% | 55.00% | 35.00% | 31.00% | 32.00% | 41.00% | 28.00% |
| high_school_biology | 310 | 85.81% | 88.06% | 78.06% | 69.03% | 86.13% | 65.81% | 69.35% | 51.94% | 44.84% | 49.35% |
| high_school_chemistry | 203 | 68.97% | 77.34% | 61.58% | 57.64% | 62.07% | 45.32% | 57.64% | 47.78% | 29.56% | 44.33% |
| high_school_computer_science | 100 | 84.00% | 86.00% | 76.00% | 74.00% | 13.00% | 59.00% | 59.00% | 59.00% | 65.00% | 47.00% |
| high_school_european_history | 165 | 81.82% | 80.61% | 80.00% | 75.76% | 84.24% | 70.91% | 66.67% | 63.64% | 20.00% | 63.64% |
| high_school_geography | 198 | 88.89% | 89.90% | 78.79% | 71.72% | 91.41% | 67.17% | 65.15% | 55.56% | 53.03% | 53.03% |
| high_school_government_and_politics | 193 | 86.01% | 85.49% | 76.68% | 65.80% | 93.78% | 63.21% | 50.26% | 51.81% | 50.78% | 55.44% |
| high_school_macroeconomics | 390 | 76.92% | 79.23% | 66.41% | 61.54% | 83.33% | 47.18% | 51.54% | 38.21% | 44.10% | 38.72% |
| high_school_mathematics | 270 | 52.59% | 48.89% | 41.11% | 44.44% | 25.93% | 32.96% | 33.70% | 37.04% | 44.44% | 26.67% |
| high_school_microeconomics | 238 | 76.89% | 82.77% | 73.95% | 67.65% | 79.83% | 53.78% | 57.98% | 44.12% | 47.90% | 42.02% |
| high_school_physics | 151 | 56.29% | 58.28% | 47.68% | 43.71% | 72.19% | 35.76% | 38.41% | 35.10% | 28.48% | 32.45% |
| high_school_psychology | 545 | 85.14% | 87.16% | 77.80% | 70.83% | 92.48% | 62.57% | 60.92% | 52.66% | 59.82% | 51.01% |
| high_school_statistics | 216 | 67.59% | 69.91% | 58.33% | 61.11% | 82.87% | 36.11% | 49.54% | 43.52% | 29.63% | 30.56% |
| high_school_us_history | 204 | 87.75% | 85.29% | 71.08% | 69.61% | 90.20% | 66.18% | 54.41% | 55.39% | 19.61% | 54.41% |
| high_school_world_history | 237 | 82.70% | 81.86% | 76.37% | 69.62% | 3.38% | 67.93% | 60.76% | 54.43% | 56.12% | 57.81% |
| human_aging | 223 | 74.44% | 74.44% | 63.23% | 60.99% | 80.27% | 55.61% | 48.43% | 49.33% | 35.43% | 47.98% |
| human_sexuality | 131 | 76.34% | 78.63% | 70.99% | 64.12% | 83.21% | 60.31% | 57.25% | 57.25% | 44.27% | 46.56% |
| international_law | 121 | 79.34% | 81.82% | 77.69% | 73.55% | 84.30% | 62.81% | 72.73% | 59.50% | 42.15% | 60.33% |
| jurisprudence | 108 | 82.41% | 80.56% | 69.44% | 70.37% | 72.22% | 60.19% | 60.19% | 54.63% | 62.96% | 45.37% |
| logical_fallacies | 163 | 76.07% | 74.23% | 69.33% | 66.87% | 64.42% | 60.12% | 48.47% | 49.69% | 65.03% | 52.76% |
| machine_learning | 112 | 66.07% | 63.39% | 48.21% | 47.32% | 8.93% | 35.71% | 27.68% | 27.68% | 36.61% | 36.61% |
| management | 103 | 82.52% | 83.50% | 80.58% | 81.55% | 79.61% | 62.14% | 69.90% | 59.22% | 66.02% | 55.34% |
| marketing | 234 | 85.90% | 88.89% | 80.77% | 80.34% | 91.88% | 73.93% | 70.94% | 70.94% | 68.80% | 66.67% |
| medical_genetics | 100 | 81.00% | 87.00% | 71.00% | 72.00% | 92.00% | 53.00% | 55.00% | 54.00% | 63.00% | 49.00% |
| miscellaneous | 783 | 82.50% | 82.12% | 71.26% | 68.20% | 11.75% | 65.39% | 50.96% | 55.68% | 61.05% | 55.94% |
| moral_disputes | 346 | 70.52% | 70.81% | 56.07% | 57.80% | 74.28% | 55.20% | 45.38% | 51.45% | 39.31% | 48.84% |
| moral_scenarios | 895 | 56.76% | 49.50% | 38.55% | 26.93% | 21.45% | 25.70% | 29.05% | 23.58% | 43.13% | 26.82% |
| nutrition | 306 | 80.07% | 76.80% | 68.63% | 63.07% | 85.29% | 55.56% | 53.27% | 50.00% | 53.27% | 44.77% |
| philosophy | 311 | 72.67% | 72.35% | 63.67% | 64.95% | 73.63% | 58.20% | 53.38% | 53.38% | 50.80% | 45.34% |
| prehistory | 324 | 79.63% | 79.32% | 65.74% | 63.89% | 86.73% | 52.47% | 49.69% | 47.22% | 58.02% | 50.93% |
| professional_accounting | 282 | 48.94% | 53.55% | 37.94% | 42.91% | 32.62% | 35.82% | 34.75% | 34.04% | 23.05% | 40.07% |
| professional_law | 1,534 | 48.50% | 47.39% | 41.59% | 39.63% | 1.11% | 35.85% | 34.75% | 33.57% | 28.49% | 36.05% |
| professional_medicine | 272 | 76.84% | 82.35% | 64.71% | 58.46% | 8.09% | 40.81% | 49.63% | 37.50% | 23.53% | 30.88% |
| professional_psychology | 612 | 70.42% | 68.63% | 57.84% | 54.25% | 43.63% | 46.41% | 42.97% | 43.30% | 44.44% | 43.46% |
| public_relations | 110 | 68.18% | 65.45% | 65.45% | 60.00% | 69.09% | 56.36% | 46.36% | 45.45% | 35.45% | 50.00% |
| security_studies | 245 | 75.10% | 72.65% | 69.80% | 64.49% | 78.37% | 63.67% | 58.37% | 55.10% | 40.82% | 53.06% |
| sociology | 201 | 82.59% | 85.07% | 77.61% | 73.63% | 83.08% | 63.18% | 66.17% | 65.17% | 66.17% | 60.70% |
| us_foreign_policy | 100 | 83.00% | 84.00% | 81.00% | 76.00% | 80.00% | 68.00% | 66.00% | 65.00% | 58.00% | 56.00% |
| virology | 166 | 53.61% | 55.42% | 52.41% | 50.00% | 54.22% | 40.36% | 43.37% | 38.55% | 34.34% | 45.18% |
| world_religions | 171 | 87.13% | 83.63% | 70.76% | 73.10% | 87.13% | 69.01% | 53.22% | 60.23% | 47.37% | 53.22% |

### D. English–Turkish gap by subject

Averaged over the five models run in both languages, sorted by gap. The range shows the smallest and largest gap among the five models.

| Subject | Category | Questions | English | Turkish | Gap (points) | Range across models |
|---|---|---:|---:|---:|---:|---|
| high_school_government_and_politics | Social sciences | 193 | 84.25% | 57.31% | −26.94 | −34.72 to −18.13 |
| college_biology | STEM | 144 | 74.17% | 48.89% | −25.28 | −31.94 to −14.58 |
| high_school_psychology | Social sciences | 545 | 83.19% | 59.60% | −23.60 | −31.74 to −15.96 |
| high_school_microeconomics | Social sciences | 238 | 73.45% | 53.11% | −20.34 | −34.03 to −8.82 |
| logical_fallacies | Humanities | 163 | 75.83% | 55.58% | −20.25 | −31.29 to −12.88 |
| astronomy | STEM | 152 | 70.92% | 51.45% | −19.47 | −23.03 to −11.18 |
| professional_psychology | Social sciences | 612 | 65.52% | 46.08% | −19.44 | −27.78 to −12.42 |
| professional_medicine | Other | 272 | 62.43% | 43.46% | −18.97 | −23.53 to −15.07 |
| high_school_macroeconomics | Social sciences | 390 | 65.90% | 47.44% | −18.46 | −31.03 to −8.97 |
| high_school_geography | Social sciences | 198 | 80.40% | 62.53% | −17.88 | −22.73 to −11.11 |
| high_school_world_history | Humanities | 237 | 79.92% | 62.11% | −17.81 | −31.65 to −7.59 |
| high_school_us_history | Humanities | 204 | 77.65% | 60.00% | −17.65 | −25.49 to −9.80 |
| miscellaneous | Other | 783 | 76.81% | 59.23% | −17.57 | −23.50 to −10.73 |
| high_school_biology | STEM | 310 | 78.58% | 61.10% | −17.48 | −26.13 to −5.81 |
| nutrition | Other | 306 | 70.78% | 53.33% | −17.45 | −23.53 to −12.42 |
| anatomy | Other | 135 | 60.15% | 43.56% | −16.59 | −20.74 to −7.41 |
| jurisprudence | Humanities | 108 | 74.44% | 58.15% | −16.30 | −24.07 to −10.19 |
| human_sexuality | Social sciences | 131 | 72.98% | 57.10% | −15.88 | −22.90 to −6.87 |
| public_relations | Social sciences | 110 | 67.27% | 51.64% | −15.64 | −23.64 to −7.27 |
| moral_disputes | Humanities | 346 | 67.05% | 51.73% | −15.32 | −21.39 to −8.09 |
| prehistory | Humanities | 324 | 67.84% | 52.84% | −15.00 | −24.69 to −7.41 |
| us_foreign_policy | Social sciences | 100 | 81.00% | 66.20% | −14.80 | −21.00 to −10.00 |
| world_religions | Humanities | 171 | 76.49% | 61.75% | −14.74 | −18.13 to −11.11 |
| human_aging | Other | 223 | 67.09% | 52.47% | −14.62 | −20.18 to −10.76 |
| sociology | Social sciences | 201 | 80.20% | 65.77% | −14.43 | −17.91 to −10.45 |
| marketing | Other | 234 | 86.84% | 72.56% | −14.27 | −17.52 to −11.97 |
| management | Other | 103 | 79.61% | 65.63% | −13.98 | −19.42 to −6.80 |
| security_studies | Social sciences | 245 | 72.65% | 58.94% | −13.71 | −20.41 to −5.31 |
| college_medicine | Other | 173 | 63.01% | 49.48% | −13.53 | −20.81 to −8.67 |
| clinical_knowledge | Other | 265 | 68.38% | 55.17% | −13.21 | −17.74 to −6.42 |
| conceptual_physics | STEM | 235 | 61.96% | 48.77% | −13.19 | −19.57 to −6.38 |
| econometrics | Social sciences | 114 | 48.95% | 36.84% | −12.11 | −17.54 to −7.02 |
| philosophy | Humanities | 311 | 67.14% | 55.05% | −12.09 | −16.72 to −7.07 |
| high_school_computer_science | STEM | 100 | 71.40% | 59.60% | −11.80 | −16.00 to −9.00 |
| computer_security | STEM | 100 | 74.20% | 62.40% | −11.80 | −21.00 to −6.00 |
| medical_genetics | Other | 100 | 68.40% | 56.60% | −11.80 | −17.00 to −7.00 |
| business_ethics | Other | 100 | 68.40% | 56.60% | −11.80 | −18.00 to −3.00 |
| professional_accounting | Other | 282 | 49.22% | 37.52% | −11.70 | −18.09 to −3.90 |
| college_computer_science | STEM | 100 | 54.00% | 42.40% | −11.60 | −16.00 to −5.00 |
| electrical_engineering | STEM | 145 | 65.52% | 54.07% | −11.45 | −14.48 to −4.14 |
| college_chemistry | STEM | 100 | 48.20% | 37.00% | −11.20 | −15.00 to −3.00 |
| high_school_statistics | STEM | 216 | 54.91% | 44.17% | −10.74 | −19.44 to −6.94 |
| international_law | Humanities | 121 | 75.87% | 65.79% | −10.08 | −14.88 to −4.96 |
| high_school_european_history | Humanities | 165 | 77.70% | 68.12% | −9.58 | −16.36 to −4.24 |
| professional_law | Humanities | 1,534 | 45.37% | 35.97% | −9.40 | −12.58 to −5.80 |
| abstract_algebra | STEM | 100 | 44.20% | 34.80% | −9.40 | −17.00 to −4.00 |
| college_physics | STEM | 102 | 40.00% | 30.78% | −9.22 | −19.61 to −4.90 |
| moral_scenarios | Humanities | 895 | 35.26% | 26.41% | −8.85 | −31.28 to +4.69 |
| machine_learning | STEM | 112 | 43.75% | 35.00% | −8.75 | −21.43 to +1.79 |
| high_school_physics | STEM | 151 | 45.43% | 37.09% | −8.34 | −13.91 to −2.65 |
| virology | Other | 166 | 51.33% | 43.49% | −7.83 | −9.04 to −6.63 |
| high_school_chemistry | STEM | 203 | 57.64% | 50.54% | −7.09 | −10.34 to −0.49 |
| elementary_mathematics | STEM | 378 | 53.44% | 46.83% | −6.61 | −11.64 to −1.06 |
| high_school_mathematics | STEM | 270 | 41.19% | 34.96% | −6.22 | −10.74 to −3.70 |
| formal_logic | Humanities | 126 | 46.35% | 43.65% | −2.70 | −9.52 to +5.56 |
| college_mathematics | STEM | 100 | 36.00% | 34.40% | −1.60 | −9.00 to +4.00 |
| global_facts | Other | 100 | 33.60% | 34.00% | +0.40 | −3.00 to +5.00 |
