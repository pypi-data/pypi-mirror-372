from abc import ABC, abstractmethod
from typing import Union

from vidur._native.entities import Batch as BatchC
from vidur._native.entities import ExecutionTime as ExecutionTimeC
from vidur._native.entities import KVParallelBatch as KVParallelBatchC
from vidur.config import BaseExecutionTimePredictorConfig, CacheConfig, ReplicaConfig
from vidur.entities import Batch, KVParallelBatch


class BaseExecutionTimePredictor(ABC):
    def __init__(
        self,
        predictor_config: BaseExecutionTimePredictorConfig,
        replica_config: ReplicaConfig,
        cache_config: CacheConfig,
    ) -> None:
        self._config = predictor_config
        self._replica_config = replica_config
        self._cache_config = cache_config
        self._model_config = replica_config.model_config

        # get configs
        self._block_size = cache_config.block_size
        self._cache_dir = predictor_config.cache_dir
        self._num_layers_per_pipeline_stage = (
            self._replica_config.num_layers_per_pipeline_stage
        )
        self._native_execution_time_predictor = None

    def get_execution_time_native(
        self, batch: Union[Batch, KVParallelBatch], pipeline_stage: int
    ) -> ExecutionTimeC:
        if isinstance(batch, KVParallelBatch):
            kvp_group_ids, batches = zip(*batch.batch_mapping.items())

            batches_native = [
                BatchC(
                    replica_id=batch.replica_id.id,
                    num_requests=len(batch.requests),
                    num_q_tokens=batch.num_q_tokens,
                    num_kv_tokens=batch.num_kv_tokens,
                    num_active_kvp_groups=batch.num_active_kvp_groups,
                    kvp_group_id=batch.kvp_group_id,
                )
                for batch in batches
            ]

            kv_parallel_batch = KVParallelBatchC(
                replica_id=batch.replica_id.id,
                kvp_group_ids=kvp_group_ids,
                batches=batches_native,
            )
            return self._native_execution_time_predictor.get_execution_time_kv_parallel_batch(
                kv_parallel_batch, pipeline_stage
            )

        batch = BatchC(
            replica_id=batch.replica_id.id,
            num_requests=len(batch.requests),
            num_q_tokens=batch.num_q_tokens,
            num_kv_tokens=batch.num_kv_tokens,
            num_active_kvp_groups=(
                batch.num_active_kvp_groups if batch.num_active_kvp_groups else []
            ),
            kvp_group_id=batch.kvp_group_id,
        )
        return self._native_execution_time_predictor.get_execution_time_batch(
            batch, pipeline_stage
        )

    def get_execution_time(
        self, batch: Union[Batch, KVParallelBatch], pipeline_stage: int
    ) -> ExecutionTimeC:
        if self._config.use_native_execution_time_predictor:
            return self.get_execution_time_native(batch, pipeline_stage)

        if isinstance(batch, KVParallelBatch):
            # take the max of all the kv group execution times
            kvp_group_execution_time = max(
                [
                    self.get_execution_time(sub_batch, pipeline_stage)
                    for sub_batch in batch.batch_mapping.values()
                ],
                key=lambda x: x.total_time,
            )
            return kvp_group_execution_time

        if pipeline_stage == self._replica_config.num_pipeline_stages - 1:
            pipeline_parallel_communication_time = 0
        else:
            pipeline_parallel_communication_time = (
                self._get_pipeline_parallel_communication_time(batch)
            )

        if self._replica_config.tensor_parallel_size == 1:
            tensor_parallel_communication_time = 0
        else:
            tensor_parallel_communication_time = (
                self._get_tensor_parallel_communication_time(batch)
            )

        # TODO(Amey): We aren't adding the kvp communication time yet
        # due to some missing data points. Even though rest of the modeling
        # code is already in place.

        return ExecutionTimeC(
            self._num_layers_per_pipeline_stage,
            self._get_attention_rope_execution_time(batch),
            self._get_attention_kv_cache_save_execution_time(batch),
            self._get_attention_decode_execution_time(batch),
            self._get_attention_prefill_execution_time(batch),
            self._get_attention_layer_pre_proj_execution_time(batch),
            self._get_attention_layer_post_proj_execution_time(batch),
            self._get_mlp_layer_up_proj_execution_time(batch),
            self._get_mlp_layer_down_proj_execution_time(batch),
            self._get_mlp_layer_act_execution_time(batch),
            self._get_attn_norm_layer_act_execution_time(batch),
            self._get_mlp_norm_layer_act_execution_time(batch),
            self._get_add_layer_act_execution_time(batch),
            tensor_parallel_communication_time,
            pipeline_parallel_communication_time,
        )

    @abstractmethod
    def _get_attention_layer_pre_proj_execution_time(self, batch: Batch) -> float:
        pass

    @abstractmethod
    def _get_attention_layer_post_proj_execution_time(self, batch: Batch) -> float:
        pass

    @abstractmethod
    def _get_attention_rope_execution_time(self, batch: Batch) -> float:
        pass

    @abstractmethod
    def _get_attention_kv_cache_save_execution_time(self, batch: Batch) -> float:
        pass

    @abstractmethod
    def _get_attention_decode_execution_time(self, batch: Batch) -> float:
        pass

    @abstractmethod
    def _get_attention_prefill_execution_time(self, batch: Batch) -> float:
        pass

    @abstractmethod
    def _get_mlp_layer_up_proj_execution_time(self, batch: Batch) -> float:
        pass

    @abstractmethod
    def _get_mlp_layer_down_proj_execution_time(self, batch: Batch) -> float:
        pass

    @abstractmethod
    def _get_mlp_layer_act_execution_time(self, batch: Batch) -> float:
        pass

    @abstractmethod
    def _get_tensor_parallel_communication_time(self, batch: Batch) -> float:
        pass

    @abstractmethod
    def _get_pipeline_parallel_communication_time(self, batch: Batch) -> float:
        pass

    @abstractmethod
    def _get_mlp_norm_layer_act_execution_time(self, batch: Batch) -> float:
        pass

    @abstractmethod
    def _get_attn_norm_layer_act_execution_time(self, batch: Batch) -> float:
        pass

    @abstractmethod
    def _get_add_layer_act_execution_time(self, batch: Batch) -> float:
        pass

    @abstractmethod
    def _get_kv_parallel_communication_time(self, batch: Batch) -> float:
        pass
