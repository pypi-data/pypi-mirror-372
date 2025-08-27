from typing import List

from vidur.entities.base_entity import BaseEntity
from vidur.entities.execution_time import ExecutionTime
from vidur.entities.request import Request
from vidur.logger import init_logger
from vidur.types import ReplicaId

logger = init_logger(__name__)


# a decorator which checks if the request has been scheduled
def check_scheduled(func):
    def wrapper(self, *args, **kwargs):
        if not self._scheduled:
            raise ValueError("Batch has not been scheduled yet")
        return func(self, *args, **kwargs)

    return wrapper


class BatchStage(BaseEntity):
    def __init__(
        self,
        batch_id: int,
        replica_id: ReplicaId,
        pipeline_stage: int,
        execution_time: ExecutionTime,
        requests: List[Request],
        num_q_tokens: List[int],
        num_kv_tokens: List[int],
        num_active_kvp_groups: List[int] = None,
        last_kvp_group_ids: List[int] = None,
        kvp_group_id: int = 0,
    ) -> None:
        self._id = BatchStage.generate_id()

        self._requests = requests
        self._num_q_tokens = num_q_tokens
        self._num_kv_tokens = num_kv_tokens
        self._num_active_kvp_groups = num_active_kvp_groups
        self._last_kvp_group_ids = last_kvp_group_ids
        self._batch_id = batch_id
        self._replica_id = replica_id
        self._pipeline_stage = pipeline_stage
        self._execution_time = execution_time
        self._kvp_group_id = kvp_group_id

        self._total_execution_time = self._execution_time.total_time
        self._model_execution_time = self._execution_time.model_time

        self._scheduled_at = None
        self._completed_at = None
        self._scheduled = False

    @property
    def num_q_tokens(self) -> List[int]:
        return self._num_q_tokens

    @property
    def num_kv_tokens(self) -> List[int]:
        return self._num_kv_tokens

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

    @property
    def request_ids(self) -> List[int]:
        return [request.id for request in self._requests]

    @property
    def requests(self) -> List[Request]:
        return self._requests

    @property
    def size(self) -> int:
        return len(self._requests)

    def on_schedule(
        self,
        time: float,
    ) -> None:
        self._scheduled_at = time
        self._scheduled = True

        if not self._last_kvp_group_ids:
            for request in self._requests:
                request.on_batch_stage_schedule(time)
            return

        for request, last_kvp_group_id in zip(self._requests, self._last_kvp_group_ids):
            if self._kvp_group_id != last_kvp_group_id:
                continue
            request.on_batch_stage_schedule(time)

    def on_stage_end(
        self,
        time: float,
    ) -> None:
        assert (
            time == self._scheduled_at + self._total_execution_time
        ), f"{time} != {self._scheduled_at} + {self._total_execution_time}"

        self._completed_at = time

        if not self._last_kvp_group_ids:
            for request, num_q_tokens in zip(self._requests, self._num_q_tokens):
                request.on_batch_stage_end(
                    time,
                    self._pipeline_stage,
                    self._total_execution_time,
                    self._model_execution_time,
                    num_q_tokens,
                )
            return

        for request, num_q_tokens, last_kvp_group_id in zip(
            self._requests, self._num_q_tokens, self._last_kvp_group_ids
        ):
            if self._kvp_group_id != last_kvp_group_id:
                continue

            request.on_batch_stage_end(
                time,
                self._pipeline_stage,
                self._total_execution_time,
                self._model_execution_time,
                num_q_tokens,
            )

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "size": self.size,
            "execution_time": self._execution_time.to_dict(),
            "scheduled_at": self._scheduled_at,
            "completed_at": self._completed_at,
            "replica_id": self._replica_id,
            "batch_id": self._batch_id,
            "pipeline_stage": self._pipeline_stage,
            "scheduled": self._scheduled,
            "request_ids": self.request_ids,
            "num_q_tokens": self.num_q_tokens,
            "num_kv_tokens": self.num_kv_tokens,
        }

    def to_chrome_trace_events(self, time: int) -> dict:
        return [
            {
                "name": f"{self.request_ids}",
                "ph": "X",
                "ts": (time - self._total_execution_time) * 1e6,
                "dur": self._total_execution_time * 1e6,
                "pid": f"replica_{self._replica_id}_kvp_group_{self._kvp_group_id}",
                "tid": self._pipeline_stage,
                "args": {
                    "batch_id": self._batch_id,
                    "batch_size": self.size,
                    "request_ids": self.request_ids,
                    "num_q_tokens": self.num_q_tokens,
                    "num_kv_tokens": self.num_kv_tokens,
                    # "execution_time": self._execution_time.to_dict(),
                    # "requests": [request.to_dict() for request in self._requests],  # slow sim time, commented out for now
                },
            }
        ]
