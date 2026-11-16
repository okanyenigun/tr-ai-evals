# Benchmark report outline

Every benchmark report in `docs/` follows this outline, whatever the task type: multiple choice, classification, open-ended generation, judged evaluation or others.

Sections marked *(if applicable)* are left out when they don't fit the benchmark. All other sections are required.

Each report is self-contained: readers shouldn't need any other document. The benchmark's README covers only code and usage.

## 1. Summary

The key findings in three to five sentences:

- what was evaluated, and on how many models
- the main results and differences between models
- the most important caveat

## 2. Benchmark

What the benchmark measures, and what it doesn't:

- **Purpose:** the capability being measured
- **Task:** what the model receives and must produce
- **Domain and language:** subject area, text type, time period, language
- **Intended use:** who the results are for and what decisions they support
- **Out of scope:** what the results shouldn't be used to claim

## 3. Data

- **Source:** origin, author and licence
- **Version:** dataset name, version and revision
- **Size:** number of items, and which splits are used
- **Composition:** how items divide across categories, e.g. subject, task type, difficulty or modality
- **Known issues:** quality problems, training data overlap risk, label errors

## 4. Evaluation method

How models are run and scored:

- **Prompting:** zero-shot or few-shot, prompt version and language
- **Generation settings:** temperature, length limits and other parameters
- **Output format:** what the model must return, and how it is parsed
- **Scoring:** how outputs are compared with references, or how they are judged
- **Judge** *(if applicable):* judge model or human raters, guidelines, agreement checks
- **Metrics:** each metric's definition and direction (higher or lower is better), with the primary metric marked
- **Invalid outputs:** how missing, malformed, truncated or refused outputs are scored
- **Baselines** *(if applicable):* chance level, human performance or reference systems

## 5. Models

One row per model:

| Column | Content |
|---|---|
| Model | Name and exact version or identifier |
| Size | Parameter count |
| Access | Open weights or API |
| Modality | Text only or multimodal |
| Notes | Quantization, special settings |

List any model that was started but not completed, with the reason.

## 6. Run environment

- **Run dates:** first and last run
- **Hardware:** for locally run models
- **Software:** model server and key library versions
- **Code version:** commit

## 7. Results

### 7.1 Overall

One row per model, sorted by the primary metric, with all metrics from section 4.

### 7.2 By category *(if applicable)*

Model × category tables, using the categories from section 3.

### 7.3 Efficiency

Time per item and total time per model. For API models, also cost.

## 8. Failures

Count and share of invalid outputs per model, by cause, e.g. truncation, malformed format, refusal or error.

## 9. Analysis

- **Observations:** notable patterns, each tied to a table in section 7 or 8
- **Examples** *(if applicable):* representative successes and failures

## 10. Limitations

Factors that limit what the results show, e.g. prompt sensitivity, training data overlap, data quality, judge bias, coverage or metrics not measured.

## 11. Reproducibility

- the command and settings used
- where the results tables come from, and how to regenerate them

## 12. Version history

Date and change for each update to the report.

## Appendix *(if applicable)*

Full prompts, complete category tables and additional examples.

## Conventions

- **File name:** `docs/reports/<benchmark>_report.md`
- **Numbers:** percentages with two decimals, e.g. 72.18%
- **Dates:** ISO format, e.g. 2026-11-16
- **Tables:** models as rows, sorted by the primary metric unless stated
