from vidur.entities.batch import Batch
from vidur.scheduler.replica_scheduler.base_replica_scheduler import (
    BaseReplicaScheduler,
)


class OrcaReplicaScheduler(BaseReplicaScheduler):
    def on_batch_end(self, batch: Batch) -> None:
        super().on_batch_end(batch)

        for request in batch.requests:
            if request.completed:
                self.free(request.id)
            else:
                self._preempted_requests.append(request)

    def _get_next_batch(self, time: float) -> Batch:
        requests = []
        num_q_tokens = []
        num_kv_tokens = []

        # all preempted_requests will have prefill completed
        while self._preempted_requests:
            if len(requests) == self._max_batch_size:
                break

            request = self._preempted_requests.pop(0)
            next_num_q_tokens = self._get_request_next_num_q_tokens(request)
            next_num_kv_tokens = request.num_processed_tokens + next_num_q_tokens
            requests.append(request)
            num_q_tokens.append(next_num_q_tokens)
            num_kv_tokens.append(next_num_kv_tokens)

        while self._request_queue:
            if len(requests) == self._max_batch_size:
                break

            if not self.can_allocate(self._max_blocks_per_sequence):
                break

            request = self._request_queue.pop(0)

            self.allocate(request.id, self._max_blocks_per_sequence)
            next_num_q_tokens = self._get_request_next_num_q_tokens(request)
            next_num_kv_tokens = request.num_processed_tokens + next_num_q_tokens
            requests.append(request)
            num_q_tokens.append(next_num_q_tokens)

        if not requests:
            return

        return Batch(self._replica_id, requests, num_q_tokens, num_kv_tokens)
