from abc import ABC, abstractmethod
from typing import List, Union

from vidur.config import (
    BaseReplicaSchedulerConfig,
    BaseRequestGeneratorConfig,
    CacheConfig,
    ReplicaConfig,
)
from vidur.entities import (
    Batch,
    BatchStage,
    KVParallelBatch,
    KVParallelBatchStage,
    Replica,
    Request,
)
from vidur.execution_time_predictor import BaseExecutionTimePredictor
from vidur.logger import init_logger
from vidur.scheduler.replica_stage_scheduler import ReplicaStageScheduler
from vidur.types import ReplicaId
from vidur.utils.memory_planner import MemoryPlanner

logger = init_logger(__name__)


class BaseReplicaScheduler(ABC):
    def __init__(
        self,
        replica_config: ReplicaConfig,
        replica_scheduler_config: BaseReplicaSchedulerConfig,
        cache_config: CacheConfig,
        request_generator_config: BaseRequestGeneratorConfig,
        replica: Replica,
        num_stages: int,
        execution_time_predictor: BaseExecutionTimePredictor,
    ) -> None:
        self._config = replica_scheduler_config
        self._replica_config = replica_config
        self._cache_config = cache_config
        self._request_generator_config = request_generator_config
        self._replica_id = replica.id
        self._num_stages = num_stages
        self._execution_time_predictor = execution_time_predictor

        self._max_blocks_per_sequence = (
            self._request_generator_config.max_tokens // self._cache_config.block_size
        )

        memory_planner = MemoryPlanner(self._replica_config, self._cache_config)

        if not self._cache_config.num_blocks:
            max_tokens = memory_planner.get_max_kv_cache_size_in_tokens()
            max_request_slots = max_tokens // self._request_generator_config.max_tokens
            self._cache_config.num_blocks = (
                self._max_blocks_per_sequence * max_request_slots
            )
        # Calculate max batch size based on available tokens per max tokens per request
        max_tokens = memory_planner.get_max_kv_cache_size_in_tokens()
        max_batch_size = max_tokens // self._request_generator_config.max_tokens
        self._max_batch_size = min(
            max_batch_size,
            self._config.batch_size_cap,
        )

        logger.debug(
            f"Obtained max batch size of {self._max_batch_size} for replica {self._replica_id}"
        )

        self._request_queue = []
        self._num_allocated_blocks = 0
        self._allocation_map = {}

        self._replica_stage_schedulers = {
            stage_id: ReplicaStageScheduler(
                replica.id,
                stage_id,
                stage_id == num_stages - 1,
                execution_time_predictor,
            )
            for stage_id in range(num_stages)
        }

        self._preempted_requests: List[Request] = []

        self._num_running_batches = 0
        self._num_running_stages = 0

    @property
    def num_pending_requests(self) -> int:
        return len(self._request_queue)

    @property
    def replica_id(self) -> ReplicaId:
        return self._replica_id

    @property
    def num_allocated_blocks(self) -> int:
        return self._num_allocated_blocks

    @property
    def memory_usage_percent(self) -> int:
        return (self._num_allocated_blocks * 100) / self._cache_config.num_blocks

    @property
    def is_sequence_pipeline_parallel_enabled(self) -> bool:
        return self._replica_config.enable_sequence_pipeline_parallel

    def is_empty(self) -> bool:
        return (
            self.num_pending_requests == 0
            and len(self._allocation_map) == 0
            and all(
                stage_scheduler.is_empty()
                for stage_scheduler in self._replica_stage_schedulers.values()
            )
        )

    def _get_request_next_num_q_tokens(self, request: Request) -> int:
        assert not request.completed

        if request.is_prefill_complete:
            return 1

        return request.num_prefill_tokens

    def _get_request_next_num_kv_tokens(
        self, request: Request, num_q_tokens: int
    ) -> int:
        return num_q_tokens + request.num_processed_tokens

    def add_request(self, request: Request) -> None:
        self._request_queue.append(request)

    def get_pending_requests(self) -> List[Request]:
        return self._request_queue

    def get_replica_stage_scheduler(self, stage_id: int):
        return self._replica_stage_schedulers[stage_id]

    def can_allocate(self, num_blocks: int) -> bool:
        return self._cache_config.num_blocks - self._num_allocated_blocks >= num_blocks

    def allocate(self, request_id: int, num_blocks: int) -> None:
        self._num_allocated_blocks += num_blocks
        if request_id not in self._allocation_map:
            self._allocation_map[request_id] = num_blocks
        else:
            self._allocation_map[request_id] += num_blocks

        assert self._num_allocated_blocks <= self._cache_config.num_blocks

    def free(self, *request_ids: List[int]) -> None:
        for request_id in request_ids:
            num_blocks = self._allocation_map.pop(request_id)
            self._num_allocated_blocks -= num_blocks

        assert self._num_allocated_blocks >= 0

    def free_batch(self, batch: Union[Batch, KVParallelBatch]) -> None:
        self.free(*batch.request_ids)

    def on_batch_end(self, batch: Union[Batch, KVParallelBatch]) -> None:
        self._num_running_batches -= 1
        assert self._num_running_batches >= 0

    def on_stage_end(
        self, stage_id: int, batch_stage: Union[BatchStage, KVParallelBatchStage]
    ) -> None:
        if not stage_id == 0:
            return

        self._num_running_stages -= 1

    @abstractmethod
    def _get_next_batch(self, time: float) -> Union[Batch, KVParallelBatch]:
        pass

    def on_schedule(self, time: float) -> Union[Batch, KVParallelBatch]:
        if not (
            self._num_running_batches < self._num_stages
            and self._num_running_stages == 0
        ):
            return None

        batch = self._get_next_batch(time)
        if not batch:
            return None

        self._num_running_batches += 1
        self._num_running_stages += 1
        return batch
