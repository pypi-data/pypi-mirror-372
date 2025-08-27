#include "vidur/entities/execution_time.h"

#include <fmt/core.h>

namespace vidur
{
namespace entities
{

ExecutionTime::ExecutionTime(
    std::size_t num_layers_per_pipeline_stage,
    double attention_rope_execution_time,
    double attention_kv_cache_save_execution_time,
    double attention_decode_execution_time,
    double attention_prefill_execution_time,
    double attention_layer_pre_proj_execution_time,
    double attention_layer_post_proj_execution_time,
    double mlp_layer_up_proj_execution_time,
    double mlp_layer_down_proj_execution_time,
    double mlp_layer_act_execution_time,
    double attn_norm_time,
    double mlp_norm_time,
    double add_time,
    double tensor_parallel_communication_time,
    double pipeline_parallel_communication_time)
    : num_layers(num_layers_per_pipeline_stage),
      attention_rope_execution_time(attention_rope_execution_time),
      attention_kv_cache_save_execution_time(
          attention_kv_cache_save_execution_time),
      attention_decode_execution_time(attention_decode_execution_time),
      attention_prefill_execution_time(attention_prefill_execution_time),
      attention_layer_pre_proj_execution_time(
          attention_layer_pre_proj_execution_time),
      attention_layer_post_proj_execution_time(
          attention_layer_post_proj_execution_time),
      mlp_layer_up_proj_execution_time(mlp_layer_up_proj_execution_time),
      mlp_layer_down_proj_execution_time(mlp_layer_down_proj_execution_time),
      mlp_layer_act_execution_time(mlp_layer_act_execution_time),
      attn_norm_time(attn_norm_time),
      mlp_norm_time(mlp_norm_time),
      add_time(add_time),
      tensor_parallel_communication_time(tensor_parallel_communication_time),
      pipeline_parallel_communication_time(
          pipeline_parallel_communication_time),
      kvp_group_communication_time(0.0)
{
}

double ExecutionTime::GetMlpLayerExecutionTime() const
{
  return mlp_layer_up_proj_execution_time + mlp_layer_down_proj_execution_time +
         mlp_layer_act_execution_time + tensor_parallel_communication_time +
         mlp_norm_time;
}

double ExecutionTime::GetAttentionLayerExecutionTime() const
{
  return attention_layer_pre_proj_execution_time +
         attention_layer_post_proj_execution_time +
         attention_rope_execution_time +
         // attention_kv_cache_save_execution_time +
         attention_decode_execution_time + attention_prefill_execution_time +
         tensor_parallel_communication_time + attn_norm_time;
}

double ExecutionTime::GetBlockExecutionTime() const
{
  return GetAttentionLayerExecutionTime() + GetMlpLayerExecutionTime() +
         add_time;
}

double ExecutionTime::GetModelTime() const
{
  // we are not counting the execution time for the embedding layer and last
  // softmax layer
  double block_execution_time = GetBlockExecutionTime();
  double pipeline_stage_execution_time = (block_execution_time * num_layers);
  // return in seconds
  return (pipeline_stage_execution_time + pipeline_parallel_communication_time +
          kvp_group_communication_time) *
         1e-3;
}

double ExecutionTime::GetModelTimeMs() const { return GetModelTime() * 1000.0; }

double ExecutionTime::GetTotalTime() const { return GetModelTime(); }

std::string ExecutionTime::ToString() const
{
  return fmt::format(
      "ExecutionTime(num_layers={}, attention_rope_execution_time={}, "
      "attention_kv_cache_save_execution_time={}, "
      "attention_decode_execution_time={}, "
      "attention_prefill_execution_time={}, "
      "attention_layer_pre_proj_execution_time={}, "
      "attention_layer_post_proj_execution_time={}, "
      "mlp_layer_up_proj_execution_time={}, "
      "mlp_layer_down_proj_execution_time={}, "
      "mlp_layer_act_execution_time={}, attn_norm_time={}, mlp_norm_time={}, "
      "add_time={}, tensor_parallel_communication_time={}, "
      "pipeline_parallel_communication_time={})",
      num_layers,
      attention_rope_execution_time,
      attention_kv_cache_save_execution_time,
      attention_decode_execution_time,
      attention_prefill_execution_time,
      attention_layer_pre_proj_execution_time,
      attention_layer_post_proj_execution_time,
      mlp_layer_up_proj_execution_time,
      mlp_layer_down_proj_execution_time,
      mlp_layer_act_execution_time,
      attn_norm_time,
      mlp_norm_time,
      add_time,
      tensor_parallel_communication_time,
      pipeline_parallel_communication_time);
}

} // namespace entities
} // namespace vidur
