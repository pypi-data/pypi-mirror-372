import heapq
from abc import abstractmethod
from collections import OrderedDict, defaultdict
from math import ceil
from typing import Any, Dict, List, Optional, Tuple, Union

from vidur.entities import (
    Batch,
    BatchStage,
    KVParallelBatch,
    KVParallelBatchStage,
    Request,
)
from vidur.logger import init_logger
from vidur.scheduler.replica_scheduler.base_replica_scheduler import (
    BaseReplicaScheduler,
)

logger = init_logger(__name__)

MAX_NUM_SKIPPED_REQUESTS = 10


class BatchFormationTracker:
    def __init__(
        self,
        replica_id: int,
        max_micro_batch_size: int,
        kv_parallel_size: int,
        max_num_tokens_per_kvp_group: int,
    ):
        self.replica_id: int = replica_id
        self.max_micro_batch_size: int = max_micro_batch_size
        self.kv_parallel_size: int = kv_parallel_size
        self.max_num_tokens_per_kvp_group: int = max_num_tokens_per_kvp_group

        self.num_requests: int = 0
        self.skipped_requests: List[Request] = []

        self.batch_requests: List[List[Request]] = [
            [] for _ in range(self.kv_parallel_size)
        ]
        self.batch_request_num_processed_tokens: List[List[int]] = [
            [] for _ in range(self.kv_parallel_size)
        ]
        self.batch_num_q_tokens: List[List[int]] = [
            [] for _ in range(self.kv_parallel_size)
        ]
        self.batch_num_kv_tokens: List[List[int]] = [
            [] for _ in range(self.kv_parallel_size)
        ]
        self.batch_num_active_kvp_groups: List[List[int]] = [
            [] for _ in range(self.kv_parallel_size)
        ]
        self.batch_last_kvp_group_ids: List[List[int]] = [
            [] for _ in range(self.kv_parallel_size)
        ]
        self.batch_total_num_q_tokens: List[int] = [
            0 for _ in range(self.kv_parallel_size)
        ]

    def _get_num_kv_tokens(
        self,
        num_processed_tokens: int,
        active_kvp_groups: List[int],
        is_last_group: bool,
    ) -> int:
        if is_last_group:
            num_kv_tokens_in_other_groups = (
                len(active_kvp_groups) - 1
            ) * self.max_num_tokens_per_kvp_group
            num_kv_tokens = num_processed_tokens - num_kv_tokens_in_other_groups
        else:
            num_kv_tokens = self.max_num_tokens_per_kvp_group

        assert num_kv_tokens >= 0

        return num_kv_tokens

    def add_request(
        self,
        request: Request,
        num_q_tokens: int,
        num_processed_tokens: int,
        active_kvp_groups: List[int],
    ) -> None:
        self.num_requests += 1

        for i, kvp_group_id in enumerate(active_kvp_groups):
            is_last_group = i == len(active_kvp_groups) - 1
            num_kv_tokens = self._get_num_kv_tokens(
                num_processed_tokens, active_kvp_groups, is_last_group
            )

            self.batch_requests[kvp_group_id].append(request)
            self.batch_num_q_tokens[kvp_group_id].append(num_q_tokens)
            self.batch_num_kv_tokens[kvp_group_id].append(num_kv_tokens)
            self.batch_num_active_kvp_groups[kvp_group_id].append(
                len(active_kvp_groups)
            )
            self.batch_request_num_processed_tokens[kvp_group_id].append(
                num_processed_tokens
            )
            self.batch_last_kvp_group_ids[kvp_group_id].append(active_kvp_groups[-1])
            self.batch_total_num_q_tokens[kvp_group_id] += num_q_tokens

    def can_add_request(self) -> bool:
        return self.num_requests < self.max_micro_batch_size

    def get_q_tokens_for_kvp_groups(self, active_kvp_groups: List[int]) -> List[int]:
        return [
            self.batch_total_num_q_tokens[kvp_group_id]
            for kvp_group_id in active_kvp_groups
        ]

    def get_batch(self) -> Optional[KVParallelBatch]:
        if self.num_requests == 0:
            return

        batch_mapping: Dict[int, Batch] = {}

        for kvp_group_id in range(self.kv_parallel_size):
            if not self.batch_num_q_tokens[kvp_group_id]:
                continue

            batch_mapping[kvp_group_id] = Batch(
                self.replica_id,
                self.batch_requests[kvp_group_id],
                self.batch_num_q_tokens[kvp_group_id],
                self.batch_num_kv_tokens[kvp_group_id],
                self.batch_num_active_kvp_groups[kvp_group_id],
                self.batch_last_kvp_group_ids[kvp_group_id],
                kvp_group_id,
            )

        return KVParallelBatch(self.replica_id, batch_mapping)


class MnemosyneBaseReplicaScheduler(BaseReplicaScheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # For vLLM and its derivatives, we only need to set a loose max batch size
        # Memory requirements are handled explicitly by the scheduler
        self._max_micro_batch_size = self._config.batch_size_cap // self._num_stages
        self._watermark_blocks = int(
            self._cache_config.watermark_blocks_fraction * self._cache_config.num_blocks
        )

        self._kv_parallel_size = self._replica_config.kv_parallel_size

        if self._kv_parallel_size > 1:
            assert (
                self._replica_config.max_num_tokens_per_kvp_group
                > self._cache_config.block_size
            ), "max_num_tokens_per_kvp_group should be greater than block_size"
            assert (
                self._replica_config.max_num_tokens_per_kvp_group
                % self._cache_config.block_size
                == 0
            ), "max_num_tokens_per_kvp_group should be a multiple of block_size"

            self._max_num_tokens_per_kvp_group = (
                self._replica_config.max_num_tokens_per_kvp_group
            )
            self._max_num_blocks_per_kvp_group = ceil(
                self._max_num_tokens_per_kvp_group / self._cache_config.block_size
            )

            assert (
                self._cache_config.num_blocks > self._max_num_blocks_per_kvp_group
            ), "num_blocks should be greater than max_num_blocks_per_kvp_group"
        else:
            self._max_num_tokens_per_kvp_group = min(
                self._request_generator_config.max_tokens,
                self._cache_config.num_blocks * self._cache_config.block_size,
            )
            self._max_num_blocks_per_kvp_group = min(
                self._max_blocks_per_sequence, self._cache_config.num_blocks
            )

        # kvp_group_id -> request_id -> num_blocks
        self._kvp_group_allocation_map: List[Dict[int, int]] = [
            defaultdict(int) for _ in range(self._kv_parallel_size)
        ]
        # kvp_group_id -> num_allocated_blocks
        self._kvp_group_num_allocated_blocks: List[int, int] = [
            0 for _ in range(self._kv_parallel_size)
        ]
        # request_id -> kvp_group_id -> num_blocks
        self._req_kvp_group_block_counter: Dict[int, OrderedDict[int, int]] = {}
        # request_id -> num_blocks
        self._req_block_counter: Dict[int, int] = defaultdict(int)
        # kvp_group -> pending prefill work
        self._kvp_group_pending_prefill_work: List[int] = [
            0 for _ in range(self._kv_parallel_size)
        ]

        # Separate queue for partial prefill requests (requests that have been scheduled at least once)
        self._partial_prefill_queue = []

    @property
    def num_pending_requests(self) -> int:
        """Override to include partial prefill requests in the count"""
        return len(self._request_queue) + len(self._partial_prefill_queue)

    @property
    def num_partial_prefill_requests(self) -> int:
        """Number of requests in partial prefill queue"""
        return len(self._partial_prefill_queue)

    def _get_batch_formation_tracker(self) -> BatchFormationTracker:
        return BatchFormationTracker(
            self._replica_id,
            self._max_micro_batch_size,
            self._kv_parallel_size,
            self._max_num_tokens_per_kvp_group,
        )

    def add_request(self, request):
        return self._request_queue.append(
            (self._get_request_priority(request), request)
        )

    def add_partial_prefill_request(self, request):
        """Add a request to the partial prefill queue with proper priority"""
        return self._partial_prefill_queue.append(
            (self._get_request_priority(request), request)
        )

    def _can_allocate_blocks(self, kvp_group_id: int, num_blocks: int) -> bool:
        return (
            self._cache_config.num_blocks
            - self._kvp_group_num_allocated_blocks[kvp_group_id]
            - num_blocks
            >= self._watermark_blocks
        )

    def allocate(self, request_id: int, num_blocks: int, kvp_group_id: int) -> None:
        self._kvp_group_allocation_map[kvp_group_id][request_id] += num_blocks

        if not request_id in self._req_kvp_group_block_counter:
            self._req_kvp_group_block_counter[request_id] = OrderedDict()

        if not kvp_group_id in self._req_kvp_group_block_counter[request_id]:
            self._req_kvp_group_block_counter[request_id][kvp_group_id] = 0

        self._req_kvp_group_block_counter[request_id][kvp_group_id] += num_blocks
        self._kvp_group_num_allocated_blocks[kvp_group_id] += num_blocks

        assert (
            self._kvp_group_num_allocated_blocks[kvp_group_id]
            <= self._cache_config.num_blocks
        )

        self._req_block_counter[request_id] += num_blocks

    def _get_allocation_order(self) -> List[int]:
        """
        We are simply picking the kvp group with the least prefill work.
        We use the square of number of prefill tokens as a simple proxy for prefill work of now.

        TODO(amey): since the initial chunks are linearly proportional to the number of tokens,
        this can lead to some inbalance in the allocation. We can improve this in the future.
        """
        return sorted(
            range(self._kv_parallel_size),
            key=lambda kvp_group_id: self._kvp_group_pending_prefill_work[kvp_group_id],
        )

    def _allocate_request(self, request: Request) -> None:
        """
        We use a naive approach to allocate memory where we allocate all the memory
        required by the request in one go. This is because we expect the compute requirement
        to far exceed the memory requirement. In KVP, incremental memory allocation can
        lead to deadlocks -- where multiple long requests are waiting for memory to be available
        on a new kvp group, but none of them can proceed because the memory is not available.

        TODO(amey): This is a naive approach and can be improved in the future. Especially, offloading
        memory allocation to CPU can be a good solution, especially for longer requests.

        While allocating memory, we must choose the kvp groups such that we have minimal
        compute contention. While also ensuring that we don't create memory hotspots.
        The allocate method offloads this responsibility to _get_allocation_order method.
        """
        if request.id in self._req_block_counter:
            return True

        if (
            request.num_prefill_tokens
            > self._kv_parallel_size * self._max_num_tokens_per_kvp_group
        ):
            logger.warn(
                f"Request {request.id} requires {request.num_prefill_tokens} tokens, which is more the kv parallel size {self._kv_parallel_size} * max num tokens per kvp group {self._max_num_tokens_per_kvp_group}"
            )
            return False

        num_required_blocks = ceil(
            request.num_prefill_tokens / self._cache_config.block_size
        )

        # more than one group is required
        num_kvp_groups = ceil(num_required_blocks / self._max_num_blocks_per_kvp_group)
        num_kvp_groups = min(num_kvp_groups, self._kv_parallel_size)
        last_group_num_blocks = (
            num_required_blocks
            - self._max_num_blocks_per_kvp_group * (num_kvp_groups - 1)
        )

        if num_kvp_groups == 1:
            for kvp_group_id in self._get_allocation_order():
                if self._can_allocate_blocks(kvp_group_id, num_required_blocks):
                    self.allocate(request.id, num_required_blocks, kvp_group_id)
                    return True
            return False

        num_kvp_groups_found = 0
        last_kvp_group_found = False

        kvp_group_ids: List[int] = []
        last_kvp_group_id: Optional[int] = None

        # check if any combination of workers can accommodate this sequence
        for kvp_group_id in self._get_allocation_order():
            """
            This loop represents a simple first-fit allocation strategy.
            """
            if self._can_allocate_blocks(
                kvp_group_id, self._max_num_blocks_per_kvp_group
            ):
                num_kvp_groups_found += 1
                kvp_group_ids.append(kvp_group_id)
            elif (
                last_group_num_blocks
                and not last_kvp_group_found
                and self._can_allocate_blocks(kvp_group_id, last_group_num_blocks)
            ):
                last_kvp_group_found = True
                num_kvp_groups_found += 1
                last_kvp_group_id = kvp_group_id

            if num_kvp_groups_found == num_kvp_groups:
                break

        if num_kvp_groups_found != num_kvp_groups:
            return False

        if last_kvp_group_id:
            kvp_group_ids.append(last_kvp_group_id)
        else:
            last_kvp_group_id = kvp_group_ids[-1]

        for kvp_group_id in kvp_group_ids:
            if kvp_group_id == last_kvp_group_id:
                self.allocate(request.id, last_group_num_blocks, kvp_group_id)
            else:
                self.allocate(
                    request.id, self._max_num_blocks_per_kvp_group, kvp_group_id
                )

            # TODO(amey): right now we are adding same weight to all the kvp groups
            # in reality later groups have lower load, also the load will be delayed
            # so we should have more work added to the earlier groups
            self._kvp_group_pending_prefill_work[kvp_group_id] += (
                request.num_prefill_tokens**2
            )

        return True

    def free(self, *request_ids: List[int]) -> None:
        for request_id in request_ids:
            for kvp_group_id in self._req_kvp_group_block_counter[request_id]:
                num_blocks = self._req_kvp_group_block_counter[request_id][kvp_group_id]
                self._kvp_group_num_allocated_blocks[kvp_group_id] -= num_blocks
                self._kvp_group_allocation_map[kvp_group_id].pop(request_id)

                assert self._kvp_group_num_allocated_blocks[kvp_group_id] >= 0

            self._req_block_counter.pop(request_id)
            self._req_kvp_group_block_counter.pop(request_id)

    def _can_append_slot(self, request: Request) -> bool:
        last_kvp_group_id = list(self._req_kvp_group_block_counter[request.id].keys())[
            -1
        ]
        return (
            self._kvp_group_num_allocated_blocks[last_kvp_group_id]
            < self._cache_config.num_blocks
        )

    def _append_slot(self, request: Request) -> None:
        num_tokens_reserved = (
            self._req_block_counter[request.id] * self._cache_config.block_size
        )
        num_tokens_required = max(0, request.num_processed_tokens - num_tokens_reserved)
        if num_tokens_required == 0:
            return

        last_kvp_group_id = list(self._req_kvp_group_block_counter[request.id].keys())[
            -1
        ]
        self.allocate(request.id, 1, last_kvp_group_id)

    def on_batch_end(self, batch: KVParallelBatch) -> None:
        super().on_batch_end(batch)

        for request in batch.requests:
            if request.completed:
                self.free(request.id)
                continue

            if not self.is_sequence_pipeline_parallel_enabled:
                if not request.is_prefill_complete:
                    self.add_partial_prefill_request(request)
                else:
                    self._preempted_requests.append(request)
            else:
                if request.is_prefill_complete:
                    self._preempted_requests.append(request)

        for kvp_group_id, sub_batch in batch.batch_mapping.items():
            for request in sub_batch.requests:
                # we need to update the prefill work for the kvp groups
                if request.num_processed_decode_tokens > 1:
                    continue

                total_work = request.num_prefill_tokens**2
                completed_work = self._get_num_processed_tokens(request) ** 2
                self._kvp_group_pending_prefill_work[kvp_group_id] = (
                    total_work - completed_work
                )

    def on_stage_end(
        self, stage_id: int, batch_stage: Union[BatchStage, KVParallelBatchStage]
    ) -> None:
        super().on_stage_end(stage_id, batch_stage)

        if not stage_id == 0:
            return

        if not self.is_sequence_pipeline_parallel_enabled:
            return

        for request in batch_stage.requests:
            assert not request.completed

            if request.is_prefill_stage_complete:
                continue

            self.add_partial_prefill_request(request)

    def _is_prefill_complete(self, request: Request) -> bool:
        if self.is_sequence_pipeline_parallel_enabled:
            return request.is_prefill_stage_complete
        else:
            return request.is_prefill_complete

    def _get_num_processed_tokens(self, request: Request) -> int:
        if self.is_sequence_pipeline_parallel_enabled:
            if not request.is_prefill_stage_complete:
                return request.num_stage_processed_tokens

            return request.num_processed_tokens
        else:
            # FIXED: Remove incorrect assertion - requests CAN complete prefill in non-SPP mode
            # The original assertion assumed prefill completion never happens in non-SPP mode, but this is incorrect
            # When num_processed_tokens > num_prefill_tokens, is_prefill_complete becomes True naturally
            return request.num_processed_tokens

    @abstractmethod
    def _get_request_next_num_q_tokens(
        self,
        time: float,
        request: Request,
        batch_formation_tracker: BatchFormationTracker,
    ) -> int:
        pass

    def get_pending_requests(self) -> List[Request]:
        """Get all pending requests including partial prefill requests"""
        return [x[1] for x in self._request_queue] + [
            x[1] for x in self._partial_prefill_queue
        ]

    def _get_active_kvp_group_ids(self, request: Request) -> List[int]:
        kvp_group_ids = list(self._req_kvp_group_block_counter[request.id].keys())

        if self._is_prefill_complete(request):
            return kvp_group_ids

        num_kvp_groups = (
            self._get_num_processed_tokens(request)
            // self._max_num_tokens_per_kvp_group
            + 1
        )

        return kvp_group_ids[:num_kvp_groups]

    def _ensure_can_append_slot(self, request: Request) -> bool:
        if self._can_append_slot(request):
            return True

        could_ensure_memory = False

        while not self._can_append_slot(request):
            if self._preempted_requests:
                last_kvp_group_id = list(
                    self._req_kvp_group_block_counter[request.id].keys()
                )[-1]
                # find the last request that contains allocation on the last kv group

                # TODO(amey): here we are just restarting the request based on the scheduling preference order
                # however, this doesn't account for the size of the request -- so potentially we could be
                # restarting a large request instead of a smaller one. We can improve this in the future.
                for i, req in enumerate(reversed(self._preempted_requests)):
                    if (
                        not last_kvp_group_id
                        in self._req_kvp_group_block_counter[req.id]
                    ):
                        continue

                    victim_request = self._preempted_requests.pop(-1 * (i + 1))
                    victim_request.restart()
                    self.free(victim_request.id)
                    self.add_request(victim_request)
                    could_ensure_memory = True
                    break
            else:
                request.restart()
                self.free(request.id)
                self.add_request(request)
                could_ensure_memory = False
                break

        return could_ensure_memory

    @abstractmethod
    def _get_request_priority(self, request: Request) -> Any:
        pass

    def _sort_request_queue(
        self, time: float, request_queue: List[Tuple[Any, Request]]
    ) -> None:
        request_queue.sort(key=lambda x: x[0])

    def _add_prefill_requests(
        self,
        time: float,
        batch_formation_tracker: BatchFormationTracker,
        request_queue: List[Tuple[Any, Request]],
    ) -> None:
        """Process requests from a queue and add them to the batch.

        Args:
            time: Current simulation time
            batch_formation_tracker: Tracker for batch formation
            request_queue: Queue of (priority, request) tuples to process
        """
        num_skipped_requests = 0

        while (
            len(request_queue) > num_skipped_requests
            and num_skipped_requests < MAX_NUM_SKIPPED_REQUESTS
        ):
            _, request = request_queue[num_skipped_requests]

            is_new_request = not request.id in self._req_block_counter

            if (
                is_new_request
                and len(self._req_block_counter) == self._config.batch_size_cap
            ):
                num_skipped_requests += 1
                continue

            assert not self._is_prefill_complete(request)

            if not batch_formation_tracker.can_add_request():
                num_skipped_requests += 1
                continue

            if not self._allocate_request(request):
                num_skipped_requests += 1
                continue

            next_num_q_tokens = self._get_request_next_num_q_tokens(
                time, request, batch_formation_tracker
            )

            if next_num_q_tokens == 0:
                num_skipped_requests += 1
                continue

            request_queue.pop(num_skipped_requests)

            active_kvp_groups = self._get_active_kvp_group_ids(request)
            num_processed_tokens = self._get_num_processed_tokens(request)
            batch_formation_tracker.add_request(
                request, next_num_q_tokens, num_processed_tokens, active_kvp_groups
            )

    def _add_running_decodes(
        self,
        batch_formation_tracker: BatchFormationTracker,
    ) -> None:
        """Add preempted requests that are ready for decode operations.

        Args:
            batch_formation_tracker: Tracker for batch formation
        """
        while self._preempted_requests:
            if not batch_formation_tracker.can_add_request():
                break

            request = self._preempted_requests.pop(0)

            assert self._is_prefill_complete(request)

            can_append_slot = self._ensure_can_append_slot(request)

            if not can_append_slot:
                # the request has been restarted and added to the wait queue
                continue

            self._append_slot(request)
            active_kvp_groups = self._get_active_kvp_group_ids(request)
            num_processed_tokens = self._get_num_processed_tokens(request)
            batch_formation_tracker.add_request(
                request, 1, num_processed_tokens, active_kvp_groups
            )

    def _get_next_batch(self, time: float) -> KVParallelBatch:
        batch_formation_tracker = self._get_batch_formation_tracker()

        # Process 'preempted requests' that are running decode
        self._add_running_decodes(batch_formation_tracker)

        # Sort both queues by priority
        self._sort_request_queue(time, self._request_queue)
        self._sort_request_queue(time, self._partial_prefill_queue)

        # Process partial prefill requests first (they have priority)
        self._add_prefill_requests(
            time, batch_formation_tracker, self._partial_prefill_queue
        )

        # Then process new requests
        self._add_prefill_requests(time, batch_formation_tracker, self._request_queue)

        batch = batch_formation_tracker.get_batch()

        return batch
