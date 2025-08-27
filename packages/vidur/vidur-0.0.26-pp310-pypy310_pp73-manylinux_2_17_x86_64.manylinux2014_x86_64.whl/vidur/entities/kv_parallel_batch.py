from typing import Dict, List

from vidur.entities.base_entity import BaseEntity
from vidur.entities.batch import Batch, check_completed, check_scheduled
from vidur.entities.batch_stage import BatchStage
from vidur.entities.execution_time import ExecutionTime
from vidur.entities.kv_parallel_batch_stage import KVParallelBatchStage
from vidur.entities.request import Request
from vidur.logger import init_logger
from vidur.types import ReplicaId

logger = init_logger(__name__)


class KVParallelBatch(BaseEntity):
    def __init__(
        self,
        replica_id: ReplicaId,
        batch_mapping: Dict[int, Batch],  # map from kvp_group_id to batch
    ) -> None:
        self._id = KVParallelBatch.generate_id()
        self._replica_id = replica_id
        self._batch_mapping = batch_mapping

        self._scheduled_at = None
        self._completed_at = None
        self._scheduled = False
        self._completed = False

        self._requests = list(
            set(sum([x.requests for x in self._batch_mapping.values()], []))
        )

        self._req_num_q_token_map = {}
        for batch in self._batch_mapping.values():
            for request, num_q_tokens in zip(batch.requests, batch.num_q_tokens):
                if request.id in self._req_num_q_token_map:
                    assert self._req_num_q_token_map[request.id] == num_q_tokens, (
                        f"Request {request.id} has different number of q tokens in different kvp groups, "
                        f"{self._req_num_q_token_map[request.id]} and {num_q_tokens}, {self.to_dict()}"
                    )
                self._req_num_q_token_map[request.id] = num_q_tokens

    @property
    def requests(self) -> List[Request]:
        return self._requests

    @property
    def replica_id(self) -> ReplicaId:
        return self._replica_id

    @property
    def batch_mapping(self) -> Dict[int, Batch]:
        return self._batch_mapping

    @property
    def creation_time(self) -> float:
        return self._creation_time

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
        return sum(x.size for x in self._batch_mapping.values())

    @property
    def request_ids(self) -> List[int]:
        return sum([x.request_ids for x in self._batch_mapping.values()], [])

    @property
    def have_all_requests_completed(self) -> bool:
        return all(
            [x.have_all_requests_completed for x in self._batch_mapping.values()]
        )

    @property
    def preempted_requests(self) -> List[Request]:
        return sum([x.preempted_requests for x in self._batch_mapping.values()], [])

    @property
    def completed_requests(self) -> List[Request]:
        return sum([x.completed_requests for x in self._batch_mapping.values()], [])

    def get_num_q_tokens_for_request(self, request_id: int) -> int:
        return self._req_num_q_token_map[request_id]

    def on_schedule(
        self,
        time: float,
    ) -> None:
        self._scheduled_at = time
        self._scheduled = True

        for batch in self._batch_mapping.values():
            batch.on_schedule(time)

    def on_batch_end(self, time: float):
        self._completed = True
        self._completed_at = time

        for batch in self._batch_mapping.values():
            batch.on_batch_end(time)

    def to_batch_stage(
        self, stage_id: int, execution_time: ExecutionTime
    ) -> KVParallelBatchStage:
        batch_stage_mapping: Dict[int, BatchStage] = {
            kvp_group_id: batch.to_batch_stage(stage_id, execution_time)
            for kvp_group_id, batch in self._batch_mapping.items()
        }
        return KVParallelBatchStage(
            self._replica_id,
            batch_stage_mapping,
            stage_id,
            execution_time,
        )

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "size": self.size,
            "replica_id": self._replica_id,
            "scheduled_at": self._scheduled_at,
            "completed_at": self._completed_at,
            "scheduled": self._scheduled,
            "batches": [batch.to_dict() for batch in self._batch_mapping.values()],
        }
