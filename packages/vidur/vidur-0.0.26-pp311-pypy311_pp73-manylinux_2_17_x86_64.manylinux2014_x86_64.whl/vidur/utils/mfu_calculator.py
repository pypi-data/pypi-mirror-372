from vidur.config import ReplicaConfig
from vidur.entities import BatchStage
from vidur.utils.param_counter import ParamCounter


class MFUCalculator:

    def __init__(self, replica_config: ReplicaConfig):
        param_counter = ParamCounter(replica_config)
        self._num_params_per_device = param_counter.get_num_parameters_per_device()

        self._num_layers_per_device = replica_config.num_layers_per_pipeline_stage
        self._num_heads_per_device = replica_config.q_heads_per_tensor_parallel_worker
        self._head_dimension = replica_config.attention_head_dim
        self._device_flops = replica_config.device_config.fp16_tflops * 2**40

    def _get_mlp_flops(self, batch_stage: BatchStage) -> float:
        num_tokens = sum(batch_stage.num_q_tokens)
        return 2 * num_tokens * self._num_params_per_device

    def _get_attention_flops(self, batch_stage: BatchStage) -> float:
        total_flops = 0
        for request, num_q_tokens, num_kv_tokens in zip(
            batch_stage.requests, batch_stage.num_q_tokens, batch_stage.num_kv_tokens
        ):
            total_flops += (
                4  # for number of ops in attention
                * self._num_layers_per_device
                * self._num_heads_per_device
                * self._head_dimension
                * num_q_tokens
                * num_kv_tokens
            )

        return total_flops

    def get_mfu(self, batch_stage: BatchStage) -> float:
        mlp_flops = self._get_mlp_flops(batch_stage)
        attention_flops = self._get_attention_flops(batch_stage)
        total_flops = mlp_flops + attention_flops
        total_flops_per_second = total_flops / batch_stage.execution_time
        return total_flops_per_second * 100 / self._device_flops
