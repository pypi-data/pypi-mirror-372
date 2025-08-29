from zsynctech_studio_sdk.models.task import TaskModel, TaskStatus
from zsynctech_studio_sdk.common.exceptions import TaskUpdateError
from zsynctech_studio_sdk.enums.operations import Operations
from zsynctech_studio_sdk.utils import get_utc_now
from zsynctech_studio_sdk.context import Context
from zsynctech_studio_sdk import client
from uuid_extensions import uuid7
from typing import Optional


EXECUTION_STATUS_COMPLETED = [
    TaskStatus.FAIL,
    TaskStatus.SUCCESS,
    TaskStatus.VALIDATION_ERROR
]


class Task:
    def __init__(self, execution_id: str, description: Optional[str] = None, code: Optional[str] = None):
        self.__task: TaskModel = TaskModel(
            executionId=execution_id,
            description=description or "Descrição não informada",
            code=code or str(uuid7()),
        )

    @property
    def task(self) -> TaskModel:
        return self.__task

    def _update(
            self,
            status: Optional[TaskStatus] = None,
            observation: Optional[str] = None,
            description: Optional[str] = None,
            code: Optional[str] = None,
            json_data: Optional[dict] = None,
        ) -> dict:
        if status in EXECUTION_STATUS_COMPLETED:
            self.task.endDate = get_utc_now()

        self.task.observation = observation if observation is not None else self.task.observation
        self.task.description = description if description is not None else self.task.description
        self.task.jsonData = json_data if json_data is not None else self.task.jsonData
        self.task.status = status if status is not None else self.task.status
        self.task.code = code if code is not None else self.task.code

        try:
            if self.task.operation == Operations.CREATE:
                response = client.post(
                    endpoint=f"{self.task.executionId}/tasks",
                    json=self.task.model_dump()
                )
            else:
                response = client.patch(
                    endpoint=f"{self.task.executionId}/tasks",
                    json=self.task.model_dump()
                )
            response.raise_for_status()
        except Exception as e:
            raise TaskUpdateError(f"Erro ao atualizar task: {str(e)}") from e

        self.task.operation = Operations.UPDATE

        return self.task.model_dump()
    
    def _start(self, observation: Optional[str] = None) -> dict:
        return self._update(status=TaskStatus.RUNNING, observation=observation)

    def fail(self, observation: Optional[str] = None) -> dict:
        return self._update(status=TaskStatus.FAIL, observation=observation)

    def validation_error(self, observation: Optional[str] = None) -> dict:
        return self._update(status=TaskStatus.VALIDATION_ERROR, observation=observation)

    def success(self, observation: Optional[str] = None) -> dict:
        return self._update(status=TaskStatus.SUCCESS, observation=observation)

    def update_json_data(self, json_data: dict) -> dict:
        return self._update(json_data=json_data)

    def update_description(self, description: str) -> dict:
        return self._update(description=description)

    def __enter__(self):
        self._start()
        Context.task = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.task.status not in EXECUTION_STATUS_COMPLETED:
            if exc_type is not None:
                self.fail(observation=str(exc_value))
            else:
                self.success()
            
        Context.task = None

        return False