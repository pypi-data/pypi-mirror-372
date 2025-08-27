from vidur.entities import Request
from vidur.logger import init_logger
from vidur.scheduler.replica_scheduler.mnemosyne_base_replica_scheduler import (
    BatchFormationTracker,
)
from vidur.scheduler.replica_scheduler.mnemosyne_lrs_replica_scheduler import (
    MnemosyneLRSReplicaScheduler,
)

logger = init_logger(__name__)

MAX_SPACE_SHARE_FRAC = 0.5


class MnemosyneSTReplicaScheduler(MnemosyneLRSReplicaScheduler):

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
        num_processed_tokens = self._get_num_processed_tokens(request)

        if num_processed_tokens < self._config.long_request_kv_cache_len_threshold:
            target_time = self._config.target_batch_time
        else:
            # avoid space sharing with another long request
            if any(
                any(
                    x > self._config.long_request_kv_cache_len_threshold
                    for x in batch_formation_tracker.batch_request_num_processed_tokens[
                        kvp_group_id
                    ]
                )
                for kvp_group_id in active_kvp_groups
            ):
                return 0

            slack_fraction = self._get_remaining_slack_fraction(time, request)
            slack_fraction = max(0.0, slack_fraction)
            slack_fraction = min(MAX_SPACE_SHARE_FRAC, slack_fraction)
            target_time = self._config.target_batch_time * (1 - slack_fraction)

        next_num_tokens = batch_formation_tracker.get_max_chunk_size_for_request(
            request,
            num_processed_tokens,
            active_kvp_groups,
            target_time,
        )

        next_num_tokens = max(0, next_num_tokens)

        return next_num_tokens
