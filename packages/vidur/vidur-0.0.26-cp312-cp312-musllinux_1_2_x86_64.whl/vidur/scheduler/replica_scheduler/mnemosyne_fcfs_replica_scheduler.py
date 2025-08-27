from typing import Any, List

from vidur.entities import Batch, Request
from vidur.execution_time_predictor.base_execution_time_predictor import (
    BaseExecutionTimePredictor,
)
from vidur.scheduler.replica_scheduler.mnemosyne_base_replica_scheduler import (
    BatchFormationTracker,
    MnemosyneBaseReplicaScheduler,
)

EXECUTION_TIME_PREDICTION_SLACK = 0.1
EXECUTION_TIME_PREDICTION_START_CHUNK_SIZE = 512
EXECUTION_TIME_PREDICTION_CHUNK_SIZE_GRANULARITY = 32
EXECUTION_TIME_PREDICTION_MAX_CHUNK_SIZE = 4096
EXECUTION_TIME_PREDICTION_MIN_CHUNK_SIZE = 32


def round_down_to_nearest_multiple(value: int, multiple: int) -> int:
    return (value // multiple) * multiple


def round_up_to_nearest_multiple(value: int, multiple: int) -> int:
    return ((value + multiple - 1) // multiple) * multiple


class BatchFormationTrackerWithRuntimePrediction(BatchFormationTracker):
    def __init__(
        self,
        replica_id: int,
        max_micro_batch_size: int,
        pipeline_parallel_size: int,
        kv_parallel_size: int,
        max_num_tokens_per_kvp_group: int,
        execution_time_predictor: BaseExecutionTimePredictor,
    ):
        super().__init__(
            replica_id,
            max_micro_batch_size,
            kv_parallel_size,
            max_num_tokens_per_kvp_group,
        )
        self.pipeline_parallel_size = pipeline_parallel_size
        self.execution_time_predictor = execution_time_predictor

        self.batch_execution_time_predictions: List[int] = [
            0 for _ in range(self.kv_parallel_size)
        ]

    def add_request(
        self,
        request: Request,
        num_q_tokens: int,
        num_processed_tokens: int,
        active_kvp_groups: List[int],
    ) -> None:
        super().add_request(
            request, num_q_tokens, num_processed_tokens, active_kvp_groups
        )

        if num_q_tokens == 1:
            # Do not update predictions for decode requests
            # We are assuming that the decode requests are all added
            # at the beginning and don't need q chunk sizes, so we can just
            # do updates once we start adding prefills
            return

        for kvp_group_id in range(self.kv_parallel_size):
            self.batch_execution_time_predictions[kvp_group_id] = (
                self._compute_batch_execution_time(kvp_group_id)
            )

    def _compute_batch_execution_time(
        self,
        kvp_group_id: int,
        extra_requests: List[Request] = [],
        extra_num_q_tokens: List[int] = [],
        extra_num_kv_tokens: List[int] = [],
        extra_num_active_kvp_groups: List[int] = [],
        extra_last_kvp_group_ids: List[int] = [],
    ) -> int:
        if len(self.batch_requests[kvp_group_id]) + len(extra_requests) == 0:
            return 0

        return (
            self.execution_time_predictor.get_execution_time(
                Batch(
                    self.replica_id,
                    self.batch_requests[kvp_group_id] + extra_requests,
                    self.batch_num_q_tokens[kvp_group_id] + extra_num_q_tokens,
                    self.batch_num_kv_tokens[kvp_group_id] + extra_num_kv_tokens,
                    self.batch_num_active_kvp_groups[kvp_group_id]
                    + extra_num_active_kvp_groups,
                    self.batch_last_kvp_group_ids[kvp_group_id]
                    + extra_last_kvp_group_ids,
                    kvp_group_id,
                ),
                pipeline_stage=0,
            ).total_time
            * self.pipeline_parallel_size
        )

    def get_batch_execution_time(self, kvp_group_id: int) -> int:
        return self.batch_execution_time_predictions[kvp_group_id]

    def get_batch_execution_time_for_kvp_groups(self, kvp_group_ids: List[int]) -> int:
        return [
            self.batch_execution_time_predictions[kvp_group_id]
            for kvp_group_id in kvp_group_ids
        ]

    def get_max_chunk_size_for_request(
        self,
        request: Request,
        num_processed_tokens: int,
        active_kvp_groups: List[int],
        target_batch_time: float,
    ) -> int:
        # identify the kvp group with the maximum execution time, and get the execution time and group id
        max_execution_time_group_id = active_kvp_groups[0]
        max_execution_time = 0

        for kvp_group_id in active_kvp_groups:
            execution_time = self.get_batch_execution_time(kvp_group_id)
            if execution_time > max_execution_time:
                max_execution_time = execution_time
                max_execution_time_group_id = kvp_group_id

        if max_execution_time > target_batch_time * (
            1 - EXECUTION_TIME_PREDICTION_SLACK
        ):
            return 0

        is_last_group = max_execution_time_group_id == active_kvp_groups[-1]

        num_kv_tokens = self._get_num_kv_tokens(
            num_processed_tokens, active_kvp_groups, is_last_group
        )
        num_kvp_groups = len(active_kvp_groups)
        last_kvp_group_id = active_kvp_groups[-1]
        remaining_tokens = max(request.num_prefill_tokens - num_processed_tokens, 0)

        # Get initial bounds for binary search
        if hasattr(request, "__last_chunk_size"):
            high = request.__last_chunk_size
        else:
            high = EXECUTION_TIME_PREDICTION_START_CHUNK_SIZE

        # Cap high by remaining tokens and the prediction limit
        high = round_down_to_nearest_multiple(
            2 * high, EXECUTION_TIME_PREDICTION_CHUNK_SIZE_GRANULARITY
        )
        high = min(remaining_tokens, high, EXECUTION_TIME_PREDICTION_MAX_CHUNK_SIZE)
        low = 0

        # Binary search with 32-token steps except for last chunk
        closest_match = 0
        closest_time = None

        seen_chunk_sizes = set()

        while low <= high:
            mid = (low + high) // 2

            if mid < remaining_tokens:
                mid = round_down_to_nearest_multiple(
                    mid, EXECUTION_TIME_PREDICTION_CHUNK_SIZE_GRANULARITY
                )
                if mid == 0:
                    mid = min(
                        remaining_tokens, EXECUTION_TIME_PREDICTION_MIN_CHUNK_SIZE
                    )
            else:
                mid = remaining_tokens
            mid = min(mid, EXECUTION_TIME_PREDICTION_MAX_CHUNK_SIZE)

            if mid in seen_chunk_sizes:
                break

            seen_chunk_sizes.add(mid)

            if mid == 0:
                break

            execution_time = self._compute_batch_execution_time(
                max_execution_time_group_id,
                extra_requests=[request],
                extra_num_q_tokens=[mid],
                extra_num_kv_tokens=[num_kv_tokens],
                extra_num_active_kvp_groups=[num_kvp_groups],
                extra_last_kvp_group_ids=[last_kvp_group_id],
            )

            # Check if execution time is within both bounds of slack range
            if execution_time >= target_batch_time * (
                1 - EXECUTION_TIME_PREDICTION_SLACK
            ) and execution_time <= target_batch_time * (
                1 + EXECUTION_TIME_PREDICTION_SLACK
            ):
                # Found a good size within slack range
                closest_match = mid
                closest_time = execution_time
                break
            elif execution_time < target_batch_time * (
                1 - EXECUTION_TIME_PREDICTION_SLACK
            ):
                low = mid
            else:
                high = mid

            if closest_time is None or abs(execution_time - target_batch_time) < abs(
                closest_time - target_batch_time
            ):
                closest_match = mid
                closest_time = execution_time

        if closest_match != 0:
            request.__last_chunk_size = closest_match

        return closest_match


class MnemosyneFCFSReplicaScheduler(MnemosyneBaseReplicaScheduler):

    def _get_batch_formation_tracker(self) -> BatchFormationTracker:
        return BatchFormationTrackerWithRuntimePrediction(
            self._replica_id,
            self._max_micro_batch_size,
            self._num_stages,
            self._kv_parallel_size,
            self._max_num_tokens_per_kvp_group,
            self._execution_time_predictor,
        )

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

        next_num_tokens = batch_formation_tracker.get_max_chunk_size_for_request(
            request,
            self._get_num_processed_tokens(request),
            active_kvp_groups,
            self._config.target_batch_time,
        )

        next_num_tokens = max(0, next_num_tokens)

        return next_num_tokens

    def _get_request_priority(self, request: Request) -> Any:
        return (request.arrived_at, request.id)
