"""Prodigy Recipe to Sentence Classification in Two Stages"""
import prodigy
from prodigy import set_hashes
from prodigy.components.db import connect
from prodigy.components.loaders import JSONL


@prodigy.recipe(
    "cls_reports",
    dataset=("The dataset to use", "positional", None, str),
    source=("The source data as a JSONL file", "positional", None, str),
)

def cls_reports(dataset: str, source: str):
    """Custom prodigy recipe"""

    def validate_answer(eg):
        answer = eg.get("user_input_a", [])
        assert 1 <= len(answer), "Confirm in text box if rating announcement is about focal firm."
        assert answer in ['y', 'n'], "Confirm by tpying 'y' (yes) or 'n' (no)."

    def add_options(stream):
        options = [
            {"id": "CS", "text": "Internal - Capital Structure"},
            {"id": "OP", "text": "Internal - Operating Performance"},
            {"id": "MA", "text": "Internal - M&A"},
            {"id": "ENV", "text": "External - Macro or Regulatory Environment"},
            {"id": "SOV", "text": "External - Sovereign Rating"},
            {"id": "MET", "text": "External - Methodology"},
            {"id": "OT", "text": "Other"},
        ]
        for task in stream:
            task["options"] = options
            yield task

    def progress(ctrl, update_return_value):
        return ctrl.total_annotated / len(list(JSONL(source)))

    def filter_stream(stream, input_hashes):
        for eg in stream:
            eg = set_hashes(eg)
            if eg["_input_hash"] not in input_hashes:
                yield eg

    input_hashes = connect().get_input_hashes(dataset)
    stream = JSONL(source)
    stream = add_options(stream)
    stream = filter_stream(stream, input_hashes)

    blocks = [
        {"view_id": "html",
         "html_template": """Supposed to be about: <b>{{meta.ric_coname}}</b><br>----------------------------<br><p>{{text}}</p>"""},
        {"view_id": "choice",
         "text": None},
        {"view_id": "text_input",
         "field_id": "user_input_a",
         "field_rows": 1,
         "field_label": "Is the rating announcement about focal firm?",
         "field_placeholder": "y / n"},
        {"view_id": "text_input",
         "field_id": "user_input_b",
         "field_rows": 3,
         "field_label": "Write a comment in case of ambiguities.",
         "field_placeholder": "Secondary:\nEvent:\nOther:"},
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
