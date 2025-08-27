from typing import Dict, List

from vidur.entities.base_entity import BaseEntity
from vidur.entities.batch_stage import BatchStage, check_scheduled
from vidur.entities.execution_time import ExecutionTime
from vidur.entities.request import Request
from vidur.logger import init_logger
from vidur.types import ReplicaId

logger = init_logger(__name__)


class KVParallelBatchStage(BaseEntity):
    def __init__(
        self,
        replica_id: ReplicaId,
        batch_stage_mapping: Dict[
            int, BatchStage
        ],  # map from kvp_group_id to batch_stage
        pipeline_stage: int,
        execution_time: ExecutionTime,
    ) -> None:
        self._id = KVParallelBatchStage.generate_id()
        self._replica_id = replica_id
        self._batch_stage_mapping = batch_stage_mapping
        self._pipeline_stage = pipeline_stage
        self._execution_time = execution_time

        self._total_execution_time = self._execution_time.total_time
        self._model_execution_time = self._execution_time.model_time

        self._scheduled_at = None
        self._completed_at = None
        self._scheduled = False

        self._requests = list(
            set(sum([x.requests for x in self._batch_stage_mapping.values()], []))
        )

    @property
    def replica_id(self) -> int:
        return self._replica_id

    @property
    def requests(self) -> List[Request]:
        return self._requests

    @property
    def batch_stage_mapping(self) -> Dict[int, BatchStage]:
        return self._batch_stage_mapping

    @property
    @check_scheduled
    def scheduled_at(self) -> float:
        return self._scheduled_at

    @property
    @check_scheduled
    def completed_at(self) -> float:
        return self._completed_at

    @property
    def execution_time(self) -> float:
        return self._total_execution_time

    @property
    def model_execution_time(self) -> float:
        return self._model_execution_time

    @property
    def pipeline_stage(self) -> int:
        return self._pipeline_stage

    def on_schedule(
        self,
        time: float,
    ) -> None:
        self._scheduled_at = time
        self._scheduled = True

        for batch_stage in self._batch_stage_mapping.values():
            batch_stage.on_schedule(time)

    def on_stage_end(
        self,
        time: float,
    ) -> None:
        self._completed_at = time

        for batch_stage in self._batch_stage_mapping.values():
            batch_stage.on_stage_end(time)

    def to_chrome_trace_events(self, time: int) -> dict:
        return sum(
            [
                batch_stage.to_chrome_trace_events(time)
                for batch_stage in self._batch_stage_mapping.values()
            ],
            [],
        )
