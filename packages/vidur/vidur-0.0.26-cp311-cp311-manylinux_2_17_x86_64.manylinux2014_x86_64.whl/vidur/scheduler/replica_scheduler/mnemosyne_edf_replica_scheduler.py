import hashlib
import os
import pickle
from typing import Any, Dict

from vidur.entities import Batch, Request
from vidur.scheduler.replica_scheduler.mnemosyne_fcfs_replica_scheduler import (
    MnemosyneFCFSReplicaScheduler,
    round_down_to_nearest_multiple,
    round_up_to_nearest_multiple,
)

PREFILL_TIME_PREDICTION_CACHE_GRANULARITY = 256
EXECUTION_TIME_PREDICTION_SLACK = 0.1
EXECUTION_TIME_PREDICTION_START_CHUNK_SIZE = 512
EXECUTION_TIME_PREDICTION_CHUNK_SIZE_GRANULARITY = 32
EXECUTION_TIME_PREDICTION_MAX_CHUNK_SIZE = 4096
EXECUTION_TIME_PREDICTION_MIN_CHUNK_SIZE = 32


class PrefillTimeCalculator:
    def __init__(
        self,
        execution_time_predictor,
        pipeline_parallel_size: int,
        kv_parallel_size: int,
        max_num_tokens_per_kvp_group: int,
        max_prefill_length: int,
        target_batch_time: float,
        enable_sequence_pipeline_parallelism: bool = False,
    ):
        self.execution_time_predictor = execution_time_predictor
        self.pipeline_parallel_size = pipeline_parallel_size
        self.kv_parallel_size = kv_parallel_size
        self.max_num_tokens_per_kvp_group = max_num_tokens_per_kvp_group
        self.target_batch_time = target_batch_time
        self.max_prefill_length = max_prefill_length
        self.enable_sequence_pipeline_parallelism = enable_sequence_pipeline_parallelism

        # Initialize cache for different prompt lengths
        cache_file_path = f"{execution_time_predictor._cache_dir}/prefill_time_cache_{self.get_hash()}.pkl"

        if os.path.exists(cache_file_path):
            with open(cache_file_path, "rb") as f:
                self.prefill_time_cache = pickle.load(f)
        else:
            self.prefill_time_cache = self._initialize_prefill_time_cache()
            with open(cache_file_path, "wb") as f:
                pickle.dump(self.prefill_time_cache, f)

    def _get_optimal_chunk_size(
        self,
        remaining_tokens: int,
        num_kvp_groups: int,
        num_kv_tokens: int,
    ) -> tuple[int, float]:
        # Binary search for optimal chunk size
        high = min(
            2 * EXECUTION_TIME_PREDICTION_START_CHUNK_SIZE,
            remaining_tokens,
            EXECUTION_TIME_PREDICTION_MAX_CHUNK_SIZE,
        )
        low = 0
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

            if mid in seen_chunk_sizes or mid == 0:
                break

            seen_chunk_sizes.add(mid)

            # TODO: this is a hack to get the execution time for a single request
            execution_time = (
                self.execution_time_predictor.get_execution_time(
                    Batch(
                        0,  # replica_id
                        [None],  # requests
                        [mid],  # num_q_tokens
                        [num_kv_tokens],  # num_kv_tokens
                        [num_kvp_groups],  # num_active_kvp_groups
                        [1],  # last_kvp_group_ids
                        0,  # kvp_group_id
                    ),
                    pipeline_stage=0,
                ).total_time
                * self.pipeline_parallel_size
            )

            # Check if execution time is within slack range
            if execution_time >= self.target_batch_time * (
                1 - EXECUTION_TIME_PREDICTION_SLACK
            ) and execution_time <= self.target_batch_time * (
                1 + EXECUTION_TIME_PREDICTION_SLACK
            ):
                closest_match = mid
                closest_time = execution_time
                break
            elif execution_time < self.target_batch_time * (
                1 - EXECUTION_TIME_PREDICTION_SLACK
            ):
                low = mid
            else:
                high = mid

            # Keep track of closest match
            if closest_time is None or abs(
                execution_time - self.target_batch_time
            ) < abs(closest_time - self.target_batch_time):
                closest_match = mid
                closest_time = execution_time

        return closest_match, closest_time

    def _calculate_total_prefill_time(
        self,
        num_prefill_tokens: int,
    ) -> float:

        total_time = 0
        current_tokens = 0

        # Process tokens in chunks until all prefill is complete
        while current_tokens < num_prefill_tokens:
            # Get active KV parallel groups for current state
            num_kvp_groups = current_tokens // self.max_num_tokens_per_kvp_group + 1
            if num_kvp_groups > 1:
                num_kv_tokens = self.max_num_tokens_per_kvp_group
            else:
                num_kv_tokens = current_tokens

            remaining = num_prefill_tokens - current_tokens

            # Find optimal chunk size for target batch time
            chunk_size, execution_time = self._get_optimal_chunk_size(
                remaining_tokens=remaining,
                num_kvp_groups=num_kvp_groups,
                num_kv_tokens=num_kv_tokens,
            )

            if chunk_size == 0:
                break

            total_time += execution_time
            current_tokens += chunk_size

        return total_time

    def _initialize_prefill_time_cache(self) -> Dict[int, float]:
        """
        Precompute execution times for different prompt lengths from
        CACHE_GRANULARITY to MAX_PROMPT_LENGTH with CACHE_GRANULARITY step size.
        """
        cache = {}
        cache[0] = 0

        for num_tokens in range(
            PREFILL_TIME_PREDICTION_CACHE_GRANULARITY,
            self.max_prefill_length + 1,
            PREFILL_TIME_PREDICTION_CACHE_GRANULARITY,
        ):
            cache[num_tokens] = self._calculate_total_prefill_time(num_tokens)

        return cache

    def get_prefill_time(
        self,
        num_prefill_tokens: int,
        num_processed_tokens: int = 0,
    ) -> float:
        """
        Calculate prefill time by using the difference between cached times
        for total tokens and processed tokens.
        """
        remaining_tokens = num_prefill_tokens - num_processed_tokens
        assert remaining_tokens > 0, "No tokens to prefill"

        # Get nearest cached sizes
        total_cached_size = round_up_to_nearest_multiple(
            num_prefill_tokens, PREFILL_TIME_PREDICTION_CACHE_GRANULARITY
        )
        processed_cached_size = round_down_to_nearest_multiple(
            num_processed_tokens, PREFILL_TIME_PREDICTION_CACHE_GRANULARITY
        )

        # Get base time from cache difference
        total_time = (
            self.prefill_time_cache[total_cached_size]
            - self.prefill_time_cache[processed_cached_size]
        )

        if self.enable_sequence_pipeline_parallelism:
            total_time = total_time / self.pipeline_parallel_size
        else:
            total_time = total_time

        return total_time

    def get_hash(self) -> str:
        attributes = {
            "pipeline_parallel_size": self.pipeline_parallel_size,
            "kv_parallel_size": self.kv_parallel_size,
            "max_num_tokens_per_kvp_group": self.max_num_tokens_per_kvp_group,
            "max_prefill_length": self.max_prefill_length,
            "target_batch_time": self.target_batch_time,
            **self.execution_time_predictor.to_dict(),
        }
        return hashlib.md5(str(attributes).encode("utf-8")).hexdigest()[0:8]


class MnemosyneEDFReplicaScheduler(MnemosyneFCFSReplicaScheduler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._prefill_time_calculator = PrefillTimeCalculator(
            self._execution_time_predictor,
            self._num_stages,
            self._kv_parallel_size,
            self._max_num_tokens_per_kvp_group,
            self._request_generator_config.max_tokens,
            self._config.target_batch_time,
            self.is_sequence_pipeline_parallel_enabled,
        )

    def add_request(self, request):
        if not hasattr(request, "deadline"):
            prefill_time = self._prefill_time_calculator.get_prefill_time(
                request.num_prefill_tokens
            )
            deadline_time = prefill_time * self._config.deadline_multiplier
            deadline_time = max(prefill_time, self._config.min_deadline)
            request.deadline = request.arrived_at + deadline_time
            request.prefill_time = prefill_time
            request.deadline_time = deadline_time
        return super().add_request(request)

    def _get_request_priority(self, request: Request) -> Any:
        return (request.deadline, request.id)
