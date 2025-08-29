"""OpenBench implementation of OpenBookQA.

OpenBookQA is an open book question answering dataset modeled after
open book exams for assessing human understanding of a subject. It consists
of 5,957 multiple-choice elementary-level science questions (4,957 train,
500 validation, 500 test), which probe the understanding of a small
"book" of 1,326 core science facts and the application of these facts
to novel situations.

Implemented by Aarush Sah
"""

from inspect_ai import Task, task
from inspect_ai.dataset import hf_dataset, Sample
from inspect_ai.scorer import choice
from inspect_ai.solver import multiple_choice


def record_to_sample(record) -> Sample:
    """Convert a HuggingFace dataset record to an Inspect Sample."""
    return Sample(
        id=record["id"],
        input=record["question_stem"],
        choices=[choice for choice in record["choices"]["text"]],
        target=record["answerKey"],
        metadata={
            # Store the choice labels in metadata for reference
            "choice_labels": record["choices"]["label"],
        },
    )


@task
def openbookqa(split: str = "validation") -> Task:
    """OpenBookQA multiple choice science question evaluation.

    Args:
        split: Dataset split to use ("train", "validation", or "test").
               Defaults to "validation".

    Returns:
        Task: Configured OpenBookQA evaluation task.
    """
    # Validate split parameter
    valid_splits = ["train", "validation", "test"]
    if split not in valid_splits:
        raise ValueError(f"Invalid split '{split}'. Must be one of {valid_splits}")

    # Load dataset from HuggingFace
    dataset = hf_dataset(
        path="allenai/openbookqa",
        split=split,
        sample_fields=record_to_sample,
        trust=True,
    )

    return Task(
        dataset=dataset,
        solver=multiple_choice(),
        scorer=choice(),
    )
