# Turkish AI Benchmarks

A collection of custom benchmarks evaluating AI models on Turkish-language tasks.

## Test 1: Turkish University Entrance Exam

The first benchmark evaluates 10 AI models on 4,895 Turkish university entrance
exam questions. The results below compare overall accuracy and valid-answer rates.

| Experiment | Model | Correct | Incorrect | Invalid / missing | Accuracy | Valid-answer rate | Accuracy among valid predictions |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | gemma3:27b | 1,231 | 3,664 | 0 | 25.15% | 100.00% | 25.15% |
| 2 | gemma4:31b | 3,535 | 1,360 | 25 | 72.22% | 99.49% | 72.59% |
| 3 | qwen3.8:27b | 4,389 | 506 | 22 | 89.66% | 99.55% | 90.07% |
| 4 | ministral-3:14b | 2,687 | 2,208 | 0 | 54.89% | 100.00% | 54.89% |
| 5 | gemma4:e4b | 3,664 | 1,231 | 0 | 74.85% | 100.00% | 74.85% |
| 6 | mistral-small3.2:latest | 2,496 | 2,399 | 0 | 50.99% | 100.00% | 50.99% |
| 7 | gemma3:4b | 1,471 | 3,424 | 0 | 30.05% | 100.00% | 30.05% |
| 8 | ornith-1.5:35b | 4,186 | 709 | 323 | 85.52% | 93.40% | 91.56% |
| 9 | muse-glimmer:30b | 4,393 | 502 | 20 | 89.74% | 99.59% | 90.11% |
| 10 | llama3.2-vision | 1,428 | 3,467 | 611 | 29.17% | 87.52% | 33.33% |
