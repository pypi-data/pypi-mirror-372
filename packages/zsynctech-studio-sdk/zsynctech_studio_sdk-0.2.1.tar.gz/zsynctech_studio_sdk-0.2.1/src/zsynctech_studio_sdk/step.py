from zsynctech_studio_sdk.models.step import StepModel, StepStatus
from zsynctech_studio_sdk.enums.operations import Operations
from zsynctech_studio_sdk.utils import get_utc_now
from zsynctech_studio_sdk.context import Context
from zsynctech_studio_sdk import client
from functools import wraps


def step(step_code: str, observation: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            if Context.task is None:
                raise Exception("Task não encontrada no contexto")

            step_model = StepModel(
                taskId=Context.task.task.id if Context.task else None,
                stepCode=step_code,
                observation=observation,
                automationOnClientId=client._instance_id,
                status=StepStatus.RUNNING,
                startDate=get_utc_now(),
            )

            response = client.post(
                endpoint=f"{Context.task.task.executionId}/taskSteps",
                json=step_model.model_dump()
            )

            response.raise_for_status()

            step_model.operation = Operations.UPDATE

            try:
                result = func(*args, **kwargs)
                step_model.status = StepStatus.SUCCESS
                step_model.endDate = get_utc_now()
                step_model.observation = step_model.observation or "Execução bem-sucedida"
                return result

            except Exception as e:
                step_model.status = StepStatus.FAIL
                step_model.endDate = get_utc_now()
                step_model.observation = str(e)
                raise

            finally:
                response = client.patch(
                    endpoint=f"{Context.task.task.executionId}/taskSteps",
                    json=step_model.model_dump()
                )
                response.raise_for_status()
        return wrapper
    return decorator
