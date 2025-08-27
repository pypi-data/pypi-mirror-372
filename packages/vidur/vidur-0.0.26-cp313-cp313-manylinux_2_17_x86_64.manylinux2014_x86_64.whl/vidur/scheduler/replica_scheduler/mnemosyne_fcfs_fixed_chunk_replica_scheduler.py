from typing import Any

from vidur.entities import Request
from vidur.scheduler.replica_scheduler.mnemosyne_base_replica_scheduler import (
    BatchFormationTracker,
    MnemosyneBaseReplicaScheduler,
)


class MnemosyneFCFSFixedChunkReplicaScheduler(MnemosyneBaseReplicaScheduler):
    def _get_request_next_num_q_tokens(
        self,
        time: float,
        request: Request,
        batch_formation_tracker: BatchFormationTracker,
    ) -> int:
        assert not request.completed

        if self._is_prefill_complete(request):
            return 1

        active_kvp_groups = self._get_active_kvp_group_ids(request)
        batched_num_q_tokens_across_groups = (
            batch_formation_tracker.get_q_tokens_for_kvp_groups(active_kvp_groups)
        )
        max_num_q_tokens_across_groups = max(batched_num_q_tokens_across_groups)

        next_num_tokens = min(
            request.num_prefill_tokens - self._get_num_processed_tokens(request),
            self._config.chunk_size - max_num_q_tokens_across_groups,
        )

        next_num_tokens = max(0, next_num_tokens)

        return next_num_tokens

    def _get_request_priority(self, request: Request) -> Any:
        return (request.arrived_at, request.id)
