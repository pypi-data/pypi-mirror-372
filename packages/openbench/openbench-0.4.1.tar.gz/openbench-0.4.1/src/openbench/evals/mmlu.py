from inspect_ai import task, Task
from inspect_ai.solver import generate
from inspect_ai.model import GenerateConfig
from openbench.datasets.mmlu import get_dataset
from openbench.scorers.mmlu import mmlu_simple_eval_scorer


@task
def mmlu(language: str = "EN-US") -> Task:
    return Task(
        dataset=get_dataset(language=language),
        solver=[generate()],
        scorer=mmlu_simple_eval_scorer(),
        name="mmlu",
        config=GenerateConfig(
            temperature=0.5,
        ),
    )
