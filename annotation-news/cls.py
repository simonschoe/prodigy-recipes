"""Prodigy Recipe to Classify News Articles"""
import prodigy
from prodigy import set_hashes
from prodigy.components.db import connect
from prodigy.components.loaders import JSONL


@prodigy.recipe(
    "cls_news",
    dataset=("The dataset to use", "positional", None, str),
    source=("The source data as a JSONL file", "positional", None, str),
)

def cls_news(dataset: str, source: str):
    """Custom prodigy recipe"""

    def validate_answer(eg):
        answer = eg.get("user_input_a", [])
        assert 1 <= len(answer), "Confirm in text box if news is about focal firm."
        assert answer in ['y', 'n'], "Confirm by typing 'y' (yes) or 'n' (no)."

    def add_options(stream):
        options = [
            {"id": "management", "text": "Change in Management Team"},
            {"id": "employee", "text": "Change in Employee Base"},
            {"id": "prod", "text": "Change in Production Capacity"},
            {"id": "strategy", "text": "Strategy Change / Plan"},
            {"id": "equity", "text": "Equity Issuance or Buyback"},
            {"id": "debt", "text": "Debt Issuance or Buyback"},
            {"id": "dividends", "text": "Dividend Announcement"},
            {"id": "madjv", "text": "M&A, Divestment, Joint Venture"},
            {"id": "aforecast", "text": "Analyst Forecast Change"},
            {"id": "mforecast", "text": "Management Forecast Change"},
            {"id": "rating", "text": "Credit Rating Event"},
            {"id": "legreg", "text": "Legal or Regulatory"},
            {"id": "filing", "text": "Quarterly or Annual Results"},
            {"id": "other", "text": "Other"},
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
         "html_template":
            """
            <p><i>About:</i> {{ric_coname}}<br><i>Rating Date:</i> {{date}}
            <br>--------------------------------------------------------------------<br>
            <b>{{title}}</b><br><i>News Date:</i> {{publication_datetime}} ({{weekday}})
            <br>--------------------------------------------------------------------<br>
            {{text}}</p>
            """
        },
        {"view_id": "choice", "text": None},
        {"view_id": "text_input",
         "field_id": "user_input_a",
         "field_rows": 1,
         "field_label": "Is the news about focal firm?",
         "field_placeholder": "y / n"},
        {"view_id": "text_input",
         "field_id": "user_input_b",
         "field_rows": 3,
         "field_label": "Write a comment in case of ambiguities.",
         "field_placeholder": ""},
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
