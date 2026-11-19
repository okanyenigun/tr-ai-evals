# Turkish AI Benchmarks

Benchmarks for evaluating AI models on Turkish-language tasks.

## Mission

Our mission is to contribute to the Turkish AI ecosystem. We give developers, researchers and organizations working in Turkish reliable evidence of how AI models perform on Turkish-language tasks. The benchmarks, code and results are public, so anyone can use them, repeat them and build on them.

## Why this project exists

Most AI benchmarks are in English, and English results say little about how a model handles Turkish.

This project evaluates models on Turkish-language tasks, the way someone choosing a model for Turkish-language work needs: reproducibly, and under the same conditions for every model.

## Principles

- **Reproducible:** every run records the exact dataset revision, prompts, settings and model weights. Published versions are never edited; changes become new versions.
- **Same conditions for every model:** all models in a benchmark get the same prompts and settings, with no tuning for any one model.

## Benchmarks

| Benchmark | What it measures | Report | Code |
|---|---|---|---|
| Turkish University Entrance Exam | Academic knowledge and reasoning, using 4,858 multiple-choice questions from ÖSS, YGS and LYS exams held in 2006–2017 | [Report](docs/reports/university_entrance_report.md) | [`university_entrance`](src/tr_ai_evals/benchmarks/university_entrance/) |
| MMLU-TR | Academic and professional knowledge across 57 subjects, using 14,042 multiple-choice questions machine-translated from MMLU, with the English originals as a baseline | [Report](docs/reports/mmlu_tr_report.md) | [`mmlu_tr`](src/tr_ai_evals/benchmarks/mmlu_tr/) |
