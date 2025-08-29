import random
from inspect_ai.dataset import Dataset, Sample, csv_dataset
from openbench.utils.text import MULTIPLE_CHOICE_PROMPT_TEMPLATE


def record_to_sample(record: dict) -> Sample:
    random.seed(0)
    options = [
        record["Correct Answer"],
        record["Incorrect Answer 1"],
        record["Incorrect Answer 2"],
        record["Incorrect Answer 3"],
    ]
    random.shuffle(options)
    # Get index of correct answer and convert to A, B, C, D
    correct_index = options.index(record["Correct Answer"])
    correct_letter = "ABCD"[correct_index]
    return Sample(
        input=MULTIPLE_CHOICE_PROMPT_TEMPLATE.format(
            prompt=record["Question"],
            option_a=options[0],
            option_b=options[1],
            option_c=options[2],
            option_d=options[3],
        ),
        target=correct_letter,
    )


def get_dataset() -> Dataset:
    return csv_dataset(
        "https://openaipublic.blob.core.windows.net/simple-evals/gpqa_diamond.csv",
        sample_fields=record_to_sample,
        auto_id=True,
        name="gpqa_simple_eval",
    )
