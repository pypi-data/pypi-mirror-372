"""
This module contains the decorators for the llm decorator.
"""

from typing import TYPE_CHECKING, Any

from pydantic_ai import models

from airflow_ai_sdk.airflow import task_decorator_factory
from airflow_ai_sdk.models.base import BaseModel
from airflow_ai_sdk.operators.llm import LLMDecoratedOperator

if TYPE_CHECKING:
    from airflow_ai_sdk.airflow import TaskDecorator


def llm(
    model: models.Model | models.KnownModelName,
    system_prompt: str,
    **kwargs: dict[str, Any],
) -> "TaskDecorator":
    """
    Decorator to make a single call to an LLM.

    Example:

    ```python
    @task.llm(model="o3-mini", system_prompt="Translate to French")
    def translate(text: str) -> str:
        return text
    ```
    """
    kwargs["model"] = model
    kwargs["system_prompt"] = system_prompt
    return task_decorator_factory(
        decorated_operator_class=LLMDecoratedOperator,
        **kwargs,
    )
