from zsynctech_studio_sdk.models.execution import ExecutionModel, ExecutionStatus
from zsynctech_studio_sdk.common.exceptions import ExecutionUpdateError
from zsynctech_studio_sdk.utils import get_utc_now
from zsynctech_studio_sdk import client
from typing import Optional, Any


EXECUTION_STATUS_COMPLETED = [
    ExecutionStatus.OUT_OF_OPERATING_HOURS,
    ExecutionStatus.INTERRUPTED,
    ExecutionStatus.FINISHED,
    ExecutionStatus.ERROR,
]


class Execution:
    def __init__(self, execution_id: Optional[str] = None):
        self.__execution_id = execution_id
        self.__execution: ExecutionModel = ExecutionModel()

        if self.execution_id:
            self.execution.id = self.execution_id

    @property
    def execution(self) -> ExecutionModel:
        return self.__execution

    @property
    def execution_id(self) -> str:
        return self.__execution_id

    @execution_id.setter
    def execution_id(self, value: str):
        self.__execution_id = value

    def _update(
            self,
            status: Optional[ExecutionStatus] = None,
            observation: Optional[str] = None,
            end_date: Optional[str] = None,
            total_task_count: Optional[int] = None,
            current_task_count: Optional[int] = None,
        ) -> dict:

        self.execution.status = status or self.execution.status
        self.execution.endDate = end_date or self.execution.endDate
        self.execution.observation = observation or self.execution.observation
        self.execution.totalTaskCount = total_task_count or self.execution.totalTaskCount
        self.execution.currentTaskCount = current_task_count or self.execution.currentTaskCount

        try:
            response = client.patch(
                endpoint=f"{self.execution_id}/executions",
                json=self.execution.model_dump()
            )
            response.raise_for_status()
        except Exception as e:
            raise ExecutionUpdateError(f"Erro ao atualizar execução: {str(e)}") from e

        return self.execution.model_dump()

    def set_total_task_count(self, total_task_count: int) -> dict[str, Any]:
        return self._update(total_task_count=total_task_count)

    def update_current_task_count(self, current_task_count: int) -> dict[str, Any]:
        return self._update(current_task_count=current_task_count)

    def update_observation(self, observation: str) -> dict[str, Any]:
        return self._update(observation=observation)

    def start(self, observation: Optional[str] = None) -> dict:
        return self._update(ExecutionStatus.RUNNING, observation)

    def error(self, observation: Optional[str] = None) -> dict:
        return self._update(ExecutionStatus.ERROR, observation=observation, end_date=get_utc_now())

    def out_of_operating_hours(self, observation: Optional[str] = None) -> dict:
        return self._update(ExecutionStatus.OUT_OF_OPERATING_HOURS, observation=observation, end_date=get_utc_now())

    def finished(self, observation: Optional[str] = None) -> dict:
        return self._update(ExecutionStatus.FINISHED, observation=observation, end_date=get_utc_now())

    def interrupted(self, observation: Optional[str] = None) -> dict:
        return self._update(ExecutionStatus.INTERRUPTED, observation=observation, end_date=get_utc_now())
