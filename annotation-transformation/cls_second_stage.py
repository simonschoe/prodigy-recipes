"""Prodigy Recipe to Classify Sentences (Second Stage)"""
import prodigy
from prodigy import set_hashes
from prodigy.components.db import connect
from prodigy.components.loaders import JSONL


@prodigy.recipe(
    "cls_second_stage",
    dataset=("The dataset to use", "positional", None, str),
    source=("The source data as a JSONL file", "positional", None, str),
)

def cls_second_stage(dataset: str, source: str):
    """Custom prodigy recipe"""

    def add_options(stream):
        options = [
            {"id": "portfolio",
             "text": "Portfolio Transformation"},
            {"id": "organizational",
             "text": "Organizational Transformation"},
            {"id": "financial",
             "text": "Financial Transformation"},
            {"id": "dontknow",
             "text": "Don't Know"},
        ]
        for task in stream:
            task["options"] = options
            yield task

    def validate_answer(eg):
        selected = eg.get("accept", [])
        assert 1 <= len(selected), "Select at least 1 option."
        assert (('dontknow' in selected) & (len(selected)== 1)) | ('dontknow' not in selected), "Select either 'Don't Know' or the relevant dimension(s)."

    def progress(ctrl, update_return_value):
        return ctrl.total_annotated / len(list(JSONL(source)))

    def filter_stream(stream, input_hashes):
        for eg in stream:
            eg = set_hashes(eg, input_keys=('text', 'DUPL'))
            if eg["_input_hash"] not in input_hashes:
                yield eg

    input_hashes = connect().get_input_hashes(dataset)
    stream = JSONL(source)
    stream = add_options(stream)
    stream = filter_stream(stream, input_hashes)

    blocks = [
        {"view_id": "html", "html_template": """<p><b>Sentence:</b><br>{{text}}</p>"""},
        {"view_id": "choice", "text": None},
        {"view_id": "text_input", "field_rows": 3, "field_label": "Write a comment or take a note if you assign 'Don't Know'."},
    ]

    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": stream,
        "config": {
            "choice_style": "multiple",
            "blocks": blocks,
        },
        "progress": progress,
        "validate_answer": validate_answer,
    }
