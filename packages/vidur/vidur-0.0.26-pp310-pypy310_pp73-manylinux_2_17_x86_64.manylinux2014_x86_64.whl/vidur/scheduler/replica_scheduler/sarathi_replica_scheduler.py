from math import ceil

from vidur.entities import Batch, BatchStage, Request
from vidur.scheduler.replica_scheduler.base_replica_scheduler import (
    BaseReplicaScheduler,
)


class SarathiReplicaScheduler(BaseReplicaScheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # For vLLM and its derivatives, we only need to set a loose max batch size
        # Memory requirements are handled explicitly by the scheduler
        self._max_micro_batch_size = self._config.batch_size_cap // self._num_stages
        self._watermark_blocks = int(
            self._cache_config.watermark_blocks_fraction * self._cache_config.num_blocks
        )

    def _can_allocate_request(self, request: Request) -> bool:
        if request.id not in self._allocation_map:
            # new request
            num_required_blocks = ceil(
                request.num_prefill_tokens / self._cache_config.block_size
            )
            return (
                self._cache_config.num_blocks
                - self._num_allocated_blocks
                - num_required_blocks
                >= self._watermark_blocks
            )

        # vllm requires at least one block to be available
        return self._cache_config.num_blocks - self._num_allocated_blocks >= 1

    def _allocate_request(self, request: Request) -> None:
        if request.id not in self._allocation_map:
            # new request
            num_required_blocks = ceil(
                request.num_prefill_tokens / self._cache_config.block_size
            )
            self.allocate(request.id, num_required_blocks)
            return

        num_tokens_reserved = (
            self._allocation_map[request.id] * self._cache_config.block_size
        )
        num_tokens_required = max(0, request.num_processed_tokens - num_tokens_reserved)

        assert (
            num_tokens_required == 0 or num_tokens_required == 1
        ), f"num_tokens_required: {num_tokens_required}"

        if num_tokens_required == 0:
            return

        self.allocate(request.id, 1)

    def on_batch_end(self, batch: Batch) -> None:
        super().on_batch_end(batch)

        for request in batch.requests:
            if request.completed:
                self.free(request.id)
                continue

            if not self.is_sequence_pipeline_parallel_enabled:
                self._preempted_requests.append(request)
            else:
                if request.is_prefill_complete:
                    self._preempted_requests.append(request)

    def on_stage_end(self, stage_id: int, batch_stage: BatchStage) -> None:
        super().on_stage_end(stage_id, batch_stage)

        if not stage_id == 0:
            return

        if not self.is_sequence_pipeline_parallel_enabled:
            return

        for request in batch_stage.requests:
            assert not request.completed

            if request.is_prefill_stage_complete:
                continue
            self._preempted_requests.append(request)

    def _is_prefill_complete(self, request: Request) -> bool:
        if self.is_sequence_pipeline_parallel_enabled:
            return request.is_prefill_stage_complete
        else:
            return request.is_prefill_complete

    def _get_num_processed_prefill_tokens(self, request: Request) -> int:
        if self.is_sequence_pipeline_parallel_enabled:
            assert not request.is_prefill_stage_complete
            return request.num_stage_processed_tokens
        else:
            assert not request.is_prefill_complete
            return request.num_processed_tokens

    def _get_request_next_num_q_tokens(
        self, request: Request, num_batch_tokens: int
    ) -> int:
        assert not request.completed

        if self._is_prefill_complete(request):
            return 1

        next_num_tokens = min(
            request.num_prefill_tokens
            - self._get_num_processed_prefill_tokens(request),
            self._config.chunk_size - num_batch_tokens,
        )

        next_num_tokens = max(0, next_num_tokens)

        return next_num_tokens

    def _get_next_batch(self, time: float) -> Batch:
        requests = []
        num_q_tokens = []
        num_kv_tokens = []
        skipped_requests = []
        running_prefills = []
        total_num_q_tokens = 0

        if self._num_running_stages != 0:
            return

        # preempted requests could contain multiple requests which have
        # partial prefills completed, so we need to be careful
        while self._preempted_requests:
            if len(requests) == self._max_micro_batch_size:
                break

            request = self._preempted_requests.pop(0)

            if not self._is_prefill_complete(request):
                running_prefills.append(request)
                continue

            next_num_q_tokens = self._get_request_next_num_q_tokens(
                request, total_num_q_tokens
            )
            next_num_kv_tokens = request.num_processed_tokens + next_num_q_tokens

            if next_num_q_tokens == 0:
                skipped_requests.append(request)
                continue

            while not self._can_allocate_request(request):
                if self._preempted_requests:
                    victim_request = self._preempted_requests.pop(-1)
                    victim_request.restart()
                    self.free(victim_request.id)
                    self._request_queue = [victim_request] + self._request_queue
                else:
                    request.restart()
                    self.free(request.id)
                    self._request_queue = [request] + self._request_queue
                    break
            else:
                self._allocate_request(request)
                assert request.is_prefill_complete
                total_num_q_tokens += next_num_q_tokens
                requests.append(request)
                num_q_tokens.append(next_num_q_tokens)
                num_kv_tokens.append(next_num_kv_tokens)

        for request in running_prefills:
            assert not request.is_prefill_complete

            next_num_q_tokens = self._get_request_next_num_q_tokens(
                request, total_num_q_tokens
            )
            next_num_kv_tokens = request.num_processed_tokens + next_num_q_tokens

            if next_num_q_tokens == 0:
                skipped_requests.append(request)
                continue

            total_num_q_tokens += next_num_q_tokens
            requests.append(request)
            num_q_tokens.append(next_num_q_tokens)
            num_kv_tokens.append(next_num_kv_tokens)

        # re-add the skipped requests, but make sure that we add them to the
        # front of the queue so that they are scheduled first and we maintain FIFO ordering
        self._preempted_requests = skipped_requests + self._preempted_requests
        self._preempted_requests = sorted(
            self._preempted_requests, key=lambda req: req.arrived_at
        )

        while self._request_queue:
            if len(self._allocation_map) == self._config.batch_size_cap:
                break

            if len(requests) == self._max_micro_batch_size:
                break

            request = self._request_queue[0]

            if not self._can_allocate_request(request):
                break

            next_num_q_tokens = self._get_request_next_num_q_tokens(
                request, total_num_q_tokens
            )
            next_num_kv_tokens = request.num_processed_tokens + next_num_q_tokens

            if next_num_q_tokens == 0:
                break

            self._request_queue.pop(0)

            self._allocate_request(request)

            # all new requests will have a prefill
            total_num_q_tokens += next_num_q_tokens
            requests.append(request)
            num_q_tokens.append(next_num_q_tokens)
            num_kv_tokens.append(next_num_kv_tokens)

        if not requests:
            return

        return Batch(self._replica_id, requests, num_q_tokens, num_kv_tokens)
