from math import ceil
from typing import List

from vidur.entities.batch import Batch, Request
from vidur.scheduler.replica_scheduler.base_replica_scheduler import (
    BaseReplicaScheduler,
)


class VLLMReplicaScheduler(BaseReplicaScheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # For vLLM and its derivatives, we only need to set a loose max batch size
        # Memory requirements are handled explicitly by the scheduler
        self._max_micro_batch_size = self._config.batch_size_cap // self._num_stages
        self._watermark_blocks = int(
            self._cache_config.watermark_blocks_fraction * self._cache_config.num_blocks
        )

    def on_batch_end(self, batch: Batch) -> None:
        super().on_batch_end(batch)

        for request in batch.requests:
            if request.completed:
                self.free(request.id)
            else:
                self._preempted_requests.append(request)

    def _can_allocate_request(self, request: Request) -> bool:
        if request.id not in self._allocation_map:
            # new request
            num_required_blocks = ceil(
                (request.num_prefill_tokens) / self._cache_config.block_size
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
                (request.num_prefill_tokens) / self._cache_config.block_size
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

    def _get_next_batch(self, time: float) -> Batch:
        requests = []
        num_q_tokens = []
        num_kv_tokens = []
        total_num_q_tokens = 0

        while self._request_queue:
            request = self._request_queue[0]

            next_num_q_tokens = self._get_request_next_num_q_tokens(request)
            next_num_kv_tokens = request.num_processed_tokens + next_num_q_tokens

            if not self._can_allocate_request(request):
                break

            if (
                total_num_q_tokens + next_num_q_tokens
                > self._config.max_tokens_in_batch
            ):
                break

            if len(self._allocation_map) == self._config.batch_size_cap:
                break

            if len(requests) == self._max_micro_batch_size:
                break

            request = self._request_queue.pop(0)

            self._allocate_request(request)
            requests.append(request)
            num_q_tokens.append(next_num_q_tokens)
            num_kv_tokens.append(next_num_kv_tokens)
            total_num_q_tokens += next_num_q_tokens

        if requests:
            return Batch(self._replica_id, requests, num_q_tokens, num_kv_tokens)

        # Safer to sort preempted_requests to maintain FIFO order
        self._preempted_requests.sort(key=lambda r: r.arrived_at)
        # all preempted_requests will have prefill completed
        while self._preempted_requests:
            if len(requests) == self._max_micro_batch_size:
                break

            request = self._preempted_requests.pop(0)

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
                next_num_q_tokens = self._get_request_next_num_q_tokens(request)
                next_num_kv_tokens = request.num_processed_tokens + next_num_q_tokens
                requests.append(request)
                num_q_tokens.append(next_num_q_tokens)
                num_kv_tokens.append(next_num_kv_tokens)

        if not requests:
            return

        return Batch(self._replica_id, requests, num_q_tokens, num_kv_tokens)
