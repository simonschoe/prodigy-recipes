"""Prodigy Recipe to Classify Sentences (Two Stages)"""
import prodigy
from prodigy import set_hashes
from prodigy.components.db import connect
from prodigy.components.loaders import JSONL


@prodigy.recipe(
    "cls_full",
    dataset=("The dataset to use", "positional", None, str),
    source=("The source data as a JSONL file", "positional", None, str),
)

def cls_full(dataset: str, source: str):
    """Custom prodigy recipe"""

    html = """<p><b>Sentence:</b><br>{{text}}</p><p><br></p><input key="{{_task_hash}}" type="radio" id="t" name="transformation" value="Transformation" onclick="(function(rb_object){window.prodigy.update({ [rb_object.name]: rb_object.id }); document.querySelector('.prodigy-options').style.display = 'block';})(this)"><label for="t"> Transformation    </label><input type="radio" id="nt" name="transformation" value="No Transformation" onclick="(function(rb_object){window.prodigy.update({ [rb_object.name]: rb_object.id }); document.querySelector('.prodigy-options').style.display = 'none'; for (const x of document.querySelectorAll('.prodigy-option')) {if (x.children[0].checked == true){x.click()}};})(this)"><label for="nt"> No Transformation    </label><input type="radio" id="dk" name="transformation" value="Don't know" onclick="(function(rb_object){window.prodigy.update({ [rb_object.name]: rb_object.id }); document.querySelector('.prodigy-options').style.display = 'none';for (const x of document.querySelectorAll('.prodigy-option')) {if (x.children[0].checked == true){x.click()}};})(this)"><label for="dk"> Don't Know</label> """

    javascript = """
    document.addEventListener('prodigymount', () => {
        const transformations = document.querySelector('.prodigy-options')
        transformations.style.display="none";
        document.addEventListener('prodigyanswer', event => {
            console.log('answered!', event.detail);
            transformations.style.display="none";});
    })
    """

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
        first_stage = eg.get("transformation", [])
        second_stage = eg.get("accept", [])
        assert 1 <= len(first_stage), "Select at least one option on first stage."
        assert (('t' == first_stage) & (len(second_stage) >= 1)) | ('t' != first_stage), "Select at least one option on second stage."
        assert (('dontknow' in second_stage) & (len(second_stage) == 1)) | ('dontknow' not in second_stage), "Select either 'Don't Know' or the relevant dimension(s)."

    def get_progress(ctrl, update_return_value):
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
        {"view_id": "html", "html_template": html},
        {"view_id": "choice", "text": None},
        {"view_id": "text_input", "field_rows": 3, "field_label": "Write a comment or take a note if you assign 'Don't Know'."}
    ]

    return {
        "view_id": "blocks",
        "dataset": dataset,
        "stream": stream,
        "config": {
            "choice_style": "multiple",
            "blocks": blocks,
            "javascript": javascript,
        },
        "progress": get_progress,
        "validate_answer": validate_answer,
    }
