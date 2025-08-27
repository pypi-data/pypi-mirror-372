from typing import List

from vidur.entities.base_entity import BaseEntity
from vidur.entities.batch_stage import BatchStage
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


def check_completed(func):
    def wrapper(self, *args, **kwargs):
        if not self._completed:
            raise ValueError("Batch has not been scheduled yet")
        return func(self, *args, **kwargs)

    return wrapper


class Batch(BaseEntity):
    def __init__(
        self,
        replica_id: ReplicaId,
        requests: List[Request],
        num_q_tokens: List[int],
        num_kv_tokens: List[int],
        num_active_kvp_groups: List[int] = None,
        last_kvp_group_ids: List[int] = None,
        kvp_group_id: int = 0,
    ) -> None:

        self._id = Batch.generate_id()
        self._replica_id = replica_id

        self._requests = requests
        self._num_q_tokens = num_q_tokens
        self._num_kv_tokens = num_kv_tokens
        self._num_active_kvp_groups = num_active_kvp_groups
        self._last_kvp_group_ids = last_kvp_group_ids
        self._kvp_group_id = kvp_group_id
        self._total_num_q_tokens = sum(num_q_tokens)
        self._total_num_kv_tokens = sum(num_kv_tokens)
        self._total_num_q_tokens_rounded = (self._total_num_q_tokens + 7) // 8 * 8
        self._num_prefill_tokens = sum(
            [
                (t if r is None or not r.is_prefill_complete else 0)
                for r, t in zip(self.requests, self._num_q_tokens)
            ]
        )

        self._scheduled_at = None
        self._completed_at = None
        self._scheduled = False
        self._completed = False

    @property
    def replica_id(self) -> int:
        return self._replica_id

    @property
    def creation_time(self) -> float:
        return self._creation_time

    @property
    def num_q_tokens(self) -> List[int]:
        return self._num_q_tokens

    @property
    def num_kv_tokens(self) -> List[int]:
        return self._num_kv_tokens

    @property
    def num_active_kvp_groups(self) -> List[int]:
        return self._num_active_kvp_groups

    @property
    def kvp_group_id(self) -> int:
        return self._kvp_group_id

    @property
    def last_kvp_group_ids(self) -> List[int]:
        return self._last_kvp_group_ids

    @property
    def total_num_q_tokens(self) -> int:
        return self._total_num_q_tokens

    @property
    def total_num_kv_tokens(self) -> int:
        return self._total_num_kv_tokens

    @property
    def total_num_q_tokens_rounded(self) -> int:
        return self._total_num_q_tokens_rounded

    @property
    def num_prefill_tokens(self) -> int:
        return self._num_prefill_tokens

    @property
    def num_decode_tokens(self) -> int:
        return self.total_num_q_tokens - self.num_prefill_tokens

    @property
    @check_scheduled
    def scheduled_at(self) -> float:
        return self._scheduled_at

    @property
    @check_completed
    def completed_at(self) -> float:
        return self._completed_at

    @property
    def completed(self) -> bool:
        return self._completed

    @property
    def scheduled(self) -> bool:
        return self._scheduled

    @property
    def size(self) -> int:
        return len(self._requests)

    @property
    def requests(self) -> List[Request]:
        return self._requests

    @property
    def request_ids(self) -> List[int]:
        return [request.id for request in self._requests]

    @property
    def have_all_requests_completed(self) -> bool:
        return all([request.completed for request in self._requests])

    def on_schedule(
        self,
        time: float,
    ) -> None:
        self._scheduled_at = time
        self._scheduled = True

        if not self._last_kvp_group_ids:
            for request in self._requests:
                request.on_batch_schedule(time)
            return

        for request, last_kvp_group_id in zip(self._requests, self._last_kvp_group_ids):
            if self._kvp_group_id != last_kvp_group_id:
                continue

            request.on_batch_schedule(time)

    def on_batch_end(self, time: float):
        self._completed = True
        self._completed_at = time

        if not self._last_kvp_group_ids:
            assert self._kvp_group_id == 0
            for request, num_q_tokens in zip(self._requests, self._num_q_tokens):
                request.on_batch_end(time, num_q_tokens)
            return

        for request, num_q_tokens, last_kvp_group_id in zip(
            self._requests, self._num_q_tokens, self._last_kvp_group_ids
        ):
            if self._kvp_group_id != last_kvp_group_id:
                continue

            request.on_batch_end(time, num_q_tokens)

    @property
    def preempted_requests(self) -> List[Request]:
        return [request for request in self._requests if request.preempted]

    @property
    def completed_requests(self) -> List[Request]:
        return [request for request in self._requests if request.completed]

    def to_batch_stage(
        self, stage_id: int, execution_time: ExecutionTime
    ) -> BatchStage:
        return BatchStage(
            self._id,
            self._replica_id,
            stage_id,
            execution_time,
            self._requests,
            self._num_q_tokens,
            self._num_kv_tokens,
            self._num_active_kvp_groups,
            self._last_kvp_group_ids,
            self._kvp_group_id,
        )

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "size": self.size,
            "replica_id": self._replica_id,
            "scheduled_at": self._scheduled_at,
            "completed_at": self._completed_at,
            "scheduled": self._scheduled,
            "request_ids": self.request_ids,
            "num_q_tokens": self.num_q_tokens,
            "num_kv_tokens": self.num_kv_tokens,
            "num_prefill_tokens": self.num_prefill_tokens,
            "num_decode_tokens": self.num_decode_tokens,
        }
