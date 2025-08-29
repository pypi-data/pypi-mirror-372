"""OpenBench implementation of SuperGPQA.
SuperGPQA: Scaling LLM Evaluation across 285 Graduate Disciplines

Implemented by Aarush Sah
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample, hf_dataset
from inspect_ai.scorer import choice, accuracy, stderr, grouped
from inspect_ai.solver import multiple_choice


def record_to_sample(record):
    """Convert a SuperGPQA record to an Inspect Sample."""
    # Create choices list from options
    choices = record["options"]

    # Create metadata dict with all extra fields
    metadata = {
        "uuid": record["uuid"],
        "discipline": record["discipline"],
        "field": record["field"],
        "subfield": record["subfield"],
        "difficulty": record["difficulty"],
        "is_calculation": record["is_calculation"],
        "answer_text": record["answer"],  # Store the full answer text
    }

    return Sample(
        input=record["question"],
        choices=choices,
        target=record["answer_letter"],  # Use the letter (A, B, C, etc.) as target
        metadata=metadata,
    )


@task
def supergpqa(
    field: str | None = None,
    subfield: str | None = None,
    difficulty: str | None = None,
    discipline: str | None = None,
):
    """SuperGPQA dataset task.

    SuperGPQA is a dataset for evaluating LLMs across 285 graduate disciplines
    with 26,529 multiple-choice questions spanning various fields including
    science, engineering, medicine, economics, and philosophy.

    Args:
        field: Filter by field (e.g., "Mathematics", "Physics", "Computer Science and Technology")
        subfield: Filter by subfield (e.g., "Mathematical Analysis", "Quantum Mechanics")
        difficulty: Filter by difficulty level ("easy", "middle", "hard")
        discipline: Filter by discipline (e.g., "Science", "Engineering", "Medicine")
    """
    # Load the full dataset
    dataset = hf_dataset(
        path="m-a-p/SuperGPQA",
        split="train",  # Only train split is available
        sample_fields=record_to_sample,
    )

    # Apply filters if specified
    if any([field, subfield, difficulty, discipline]):

        def filter_fn(sample):
            if field and sample.metadata.get("field") != field:
                return False
            if subfield and sample.metadata.get("subfield") != subfield:
                return False
            if difficulty and sample.metadata.get("difficulty") != difficulty:
                return False
            if discipline and sample.metadata.get("discipline") != discipline:
                return False
            return True

        dataset = dataset.filter(filter_fn)

    return Task(
        dataset=dataset,
        solver=multiple_choice(),
        scorer=choice(),
        metrics=[
            # Overall metrics
            accuracy(),
            stderr(),
            # Metrics grouped by difficulty
            grouped(accuracy(), "difficulty"),
            grouped(stderr(), "difficulty"),
        ],
    )
