"""Gradio interface and Hugging Face Spaces entry point."""

import json
from pathlib import Path

import gradio as gr
import pandas as pd

from tr_ai_evals.localization import (
    course_label,
    header_label,
    localized_table,
    row_summary,
    text,
)
from tr_ai_evals.results import BenchmarkResults, csv_download

DATA_ROOT = Path(__file__).resolve().parent / "data"
ORDER = ["Highest first", "Lowest first"]


def create_app(data_root: Path | None = None):
    data_root = data_root if data_root is not None else DATA_ROOT
    catalog = json.loads((data_root / "benchmarks.json").read_text(encoding="utf-8"))
    if not catalog:
        raise ValueError("The benchmark catalog must contain at least one benchmark.")
    benchmarks = {
        key: BenchmarkResults.from_directory(data_root / entry["directory"])
        for key, entry in catalog.items()
    }
    default_benchmark = next(iter(catalog))
    translations = []
    panels = []

    def localized(component_type, **properties):
        """Register translated properties without replacing a component's state."""
        dynamic = {key: value for key, value in properties.items() if callable(value)}
        initial = {
            key: value("TR", default_benchmark) if callable(value) else value
            for key, value in properties.items()
        }
        component = component_type(**initial)
        if dynamic:
            translations.append((component, dynamic))
        return component

    def label(key):
        return lambda language, benchmark: text(key, language)

    def model_filter():
        return localized(
            gr.Dropdown,
            choices=lambda language, benchmark: benchmarks[benchmark].models,
            value=[],
            multiselect=True,
            min_width=240,
            label=label("models"),
            info=label("models_help"),
        )

    def course_filter():
        return localized(
            gr.Dropdown,
            choices=lambda language, benchmark: [
                (course_label(course, language), course)
                for course in benchmarks[benchmark].courses
            ],
            value=[],
            multiselect=True,
            min_width=240,
            label=label("courses"),
            info=label("courses_help"),
        )

    def accuracy_filter():
        return localized(
            gr.Slider,
            minimum=0,
            maximum=100,
            value=0,
            step=1,
            min_width=240,
            label=label("minimum"),
        )

    def sort_filter(columns, courses=False):
        return localized(
            gr.Dropdown,
            choices=lambda language, benchmark: [
                (header_label(column, language), column)
                for column in columns(benchmarks[benchmark])
            ],
            value="Course" if courses else "Accuracy",
            min_width=240,
            label=label("sort_courses" if courses else "sort"),
            info=label("sort_courses_help") if courses else None,
        )

    def order_filter(default):
        return localized(
            gr.Radio,
            choices=lambda language, benchmark: [
                (text("descending", language), ORDER[0]),
                (text("ascending", language), ORDER[1]),
            ],
            value=default,
            label=label("order"),
            min_width=240,
        )

    def table_panel(query_name, inputs, defaults, name, language, benchmark):
        def query_table(values, selected_language, selected_benchmark):
            query = getattr(benchmarks[selected_benchmark], query_name)
            return localized_table(
                query(*values),
                selected_language,
                sort_by=values[-2],
                ascending=values[-1] == ORDER[1],
            )

        initial = query_table(defaults, "TR", default_benchmark)
        summary = gr.Markdown(row_summary(len(initial), "TR"))
        table = localized(
            gr.Dataframe,
            value=initial,
            datatype=[
                "number" if pd.api.types.is_numeric_dtype(initial[column]) else "str"
                for column in initial
            ],
            interactive=False,
            label=label("results"),
            show_label=False,
            max_height=650,
            wrap=False,
            buttons=["fullscreen", "copy"],
        )
        with gr.Row():
            reset = localized(gr.Button, value=label("reset"), size="sm")
            download = localized(
                gr.DownloadButton,
                label=label("download"),
                value=csv_download(initial, name),
                size="sm",
                variant="primary",
            )

        def update_results(*values):
            selected_language, selected_benchmark = values[-2:]
            result = query_table(values[:-2], selected_language, selected_benchmark)
            return (
                result,
                row_summary(len(result), selected_language),
                csv_download(result, name),
            )

        gr.on(
            triggers=[component.change for component in [*inputs, language]],
            fn=update_results,
            inputs=[*inputs, language, benchmark],
            outputs=[table, summary, download],
            api_name=name,
        )
        reset.click(fn=lambda: defaults, outputs=inputs, api_name=False)
        panels.append((inputs, defaults, query_table, table, summary, download, name))

    def benchmark_stats(language, benchmark):
        results = benchmarks[benchmark]
        questions = f"{int(results.overall['Questions'].iloc[0]):,}"
        if language == "TR":
            questions = questions.replace(",", ".")
        stats = text("stats", language).format(
            models=len(results.models),
            questions=questions,
            courses=len(results.courses),
        )
        return stats

    with gr.Blocks(title=text("title"), delete_cache=(3600, 3600)) as demo:
        with gr.Row():
            localized(
                gr.Markdown,
                value=lambda language, benchmark: (
                    f"# {text('title', language)}\n{text('intro', language)}"
                ),
                scale=5,
            )
            language = gr.Radio(
                ["TR", "EN"], value="TR", label="Dil / Language", scale=1, min_width=150
            )
        benchmark = localized(
            gr.Dropdown,
            choices=lambda language, selected: [
                (entry["titles"][language], key) for key, entry in catalog.items()
            ],
            value=default_benchmark,
            label=label("benchmark"),
            filterable=False,
        )
        localized(gr.Markdown, value=benchmark_stats)
        with localized(gr.Tab, label=label("overall")):
            with gr.Row():
                models = model_filter()
                minimum = accuracy_filter()
            with gr.Row():
                sort = sort_filter(
                    lambda results: [
                        column for column in results.overall if column != "Questions"
                    ]
                )
                order = order_filter(ORDER[0])
            table_panel(
                "overall_results",
                [models, minimum, sort, order],
                [[], 0, "Accuracy", ORDER[0]],
                "overall",
                language,
                benchmark,
            )
        with localized(gr.Tab, label=label("course_accuracy")):
            with gr.Row():
                courses = course_filter()
                models = model_filter()
            with gr.Row():
                sort = sort_filter(
                    lambda results: ["Course", "Questions", *results.models],
                    courses=True,
                )
                order = order_filter(ORDER[1])
            table_panel(
                "course_results",
                [courses, models, sort, order],
                [[], [], "Course", ORDER[1]],
                "course_accuracy",
                language,
                benchmark,
            )

        def translated_updates(selected_language, selected_benchmark):
            return {
                component: {
                    key: value(selected_language, selected_benchmark)
                    for key, value in properties.items()
                }
                for component, properties in translations
            }

        def switch_language(selected_language, selected_benchmark):
            return [
                gr.update(**properties)
                for properties in translated_updates(
                    selected_language, selected_benchmark
                ).values()
            ]

        language.change(
            fn=switch_language,
            inputs=[language, benchmark],
            outputs=[component for component, _ in translations],
            api_name=False,
        )

        benchmark_outputs = [component for component, _ in translations] + [
            panel[4] for panel in panels
        ]

        def switch_benchmark(selected_language, selected_benchmark):
            updates = translated_updates(selected_language, selected_benchmark)
            for inputs, defaults, query_table, table, summary, download, name in panels:
                for component, default in zip(inputs, defaults):
                    updates[component]["value"] = default
                result = query_table(defaults, selected_language, selected_benchmark)
                updates[table]["value"] = result
                updates[summary] = {
                    "value": row_summary(len(result), selected_language)
                }
                updates[download]["value"] = csv_download(result, name)
            return [gr.update(**updates[component]) for component in benchmark_outputs]

        benchmark.change(
            fn=switch_benchmark,
            inputs=[language, benchmark],
            outputs=benchmark_outputs,
            api_name=False,
        )
    return demo


if __name__ == "__main__":
    create_app().launch(theme=gr.themes.Soft(primary_hue="teal"), footer_links=[])
