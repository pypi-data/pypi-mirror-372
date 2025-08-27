#include "vidur/execution_time_predictor/execution_time_predictor.h"

#include <algorithm>
#include <cassert>
#include <cmath>

namespace vidur
{
namespace execution_time_predictor
{

ExecutionTimePredictor::ExecutionTimePredictor(
    const config::ExecutionTimePredictorConfig config,
    const config::ReplicaConfig replica_config,
    const config::ModelConfig model_config,
    const std::vector<std::string>& prediction_ops,
    const std::vector<std::vector<PredictionKey>>& prediction_keys,
    const std::vector<std::vector<double>>& prediction_values,
    const std::string& hash)
    : config_(config),
      replica_config_(replica_config),
      model_config_(model_config),
      hash_(hash),
      num_layers_per_pipeline_stage_(
          model_config.num_layers / replica_config.num_pipeline_stages)
{
  assert(prediction_ops.size() == prediction_keys.size());
  assert(prediction_ops.size() == prediction_values.size());

  predictions_.reserve(prediction_ops.size());
  for (std::size_t i = 0; i < prediction_ops.size(); i++)
  {
    assert(prediction_keys[i].size() == prediction_values[i].size());

    predictions_[prediction_ops[i]] =
        std::unordered_map<PredictionKey, double, PairHash>();
    predictions_[prediction_ops[i]].reserve(prediction_keys[i].size());
    for (std::size_t j = 0; j < prediction_keys[i].size(); j++)
    {
      predictions_[prediction_ops[i]][prediction_keys[i][j]] =
          prediction_values[i][j];
    }
  }
}

entities::ExecutionTime ExecutionTimePredictor::GetExecutionTimeBatch(
    const entities::Batch& batch,
    std::size_t pipeline_stage) const
{
  double pipeline_parallel_communication_time = 0.0;
  if (pipeline_stage != replica_config_.num_pipeline_stages - 1)
  {
    pipeline_parallel_communication_time =
        GetPipelineParallelCommunicationTime(batch);
  }

  double tensor_parallel_communication_time = 0.0;
  if (replica_config_.tensor_parallel_size == 1)
  {
    tensor_parallel_communication_time = 0.0;
  }
  else
  {
    tensor_parallel_communication_time =
        GetTensorParallelCommunicationTime(batch);
  }

  // TODO: Add kv_parallel communication time

  return entities::ExecutionTime(
      num_layers_per_pipeline_stage_,
      GetAttentionRopeExecutionTime(batch),
      GetAttentionKvCacheSaveExecutionTime(batch),
      GetAttentionDecodeExecutionTime(batch),
      GetAttentionPrefillExecutionTime(batch),
      GetAttentionLayerPreProjExecutionTime(batch),
      GetAttentionLayerPostProjExecutionTime(batch),
      GetMlpLayerUpProjExecutionTime(batch),
      GetMlpLayerDownProjExecutionTime(batch),
      GetMlpLayerActExecutionTime(batch),
      GetAttnNormLayerActExecutionTime(batch),
      GetMlpNormLayerActExecutionTime(batch),
      GetAddLayerActExecutionTime(batch),
      tensor_parallel_communication_time,
      pipeline_parallel_communication_time);
}

entities::ExecutionTime ExecutionTimePredictor::GetExecutionTimeKVParallelBatch(
    const entities::KVParallelBatch& kvp_batch,
    std::size_t pipeline_stage) const
{
  auto it = std::max_element(
      kvp_batch.batch_mapping.begin(),
      kvp_batch.batch_mapping.end(),
      [&](const auto& a, const auto& b)
      {
        return GetExecutionTimeBatch(*(a.second), pipeline_stage)
                   .GetTotalTime() <
               GetExecutionTimeBatch(*(b.second), pipeline_stage)
                   .GetTotalTime();
      });

  return GetExecutionTimeBatch(*(it->second), pipeline_stage);
}

double ExecutionTimePredictor::GetAttentionLayerPreProjExecutionTime(
    const entities::Batch& batch) const
{
  return predictions_.at(PredictionOps::ATTN_PRE_PROJ)
      .at(GetPredictionKey(batch.total_num_q_tokens_rounded));
}

double ExecutionTimePredictor::GetAttentionLayerPostProjExecutionTime(
    const entities::Batch& batch) const
{
  return predictions_.at(PredictionOps::ATTN_POST_PROJ)
      .at(GetPredictionKey(batch.total_num_q_tokens_rounded));
}

double ExecutionTimePredictor::GetAttentionRopeExecutionTime(
    const entities::Batch& batch) const
{
  return predictions_.at(PredictionOps::ATTN_ROPE)
      .at(GetPredictionKey(batch.total_num_q_tokens_rounded));
}

double ExecutionTimePredictor::GetAttentionKvCacheSaveExecutionTime(
    const entities::Batch& batch) const
{
  return predictions_.at(PredictionOps::ATTN_KV_CACHE_SAVE)
      .at(GetPredictionKey(batch.total_num_q_tokens_rounded));
}

double ExecutionTimePredictor::GetAttentionDecodeExecutionTime(
    const entities::Batch& batch) const
{
  auto [decode_batch_size, decode_avg_kv_cache_size] =
      GetBatchDecodeAttentionParams(batch);

  if (decode_batch_size == 0)
  {
    return 0.0;
  }

  return predictions_.at(PredictionOps::ATTN_DECODE)
             .at(GetPredictionKey(
                 decode_batch_size,
                 decode_avg_kv_cache_size)) *
         (1 + config_.attention_decode_batching_overhead_fraction *
                  (decode_batch_size > 1 ? 1 : 0));
}

double ExecutionTimePredictor::GetAttentionPrefillExecutionTime(
    const entities::Batch& batch) const
{
  std::vector<std::pair<int, int>> prefill_params =
      GetBatchPrefillAttentionParams(batch);

  if (prefill_params.empty())
  {
    return 0.0;
  }

  double total_time = 0.0;
  for (const auto& [kv_cache_size, prefill_chunk_size] : prefill_params)
  {
    std::size_t prefill_chunk_size_rounded =
        ((prefill_chunk_size + 31) / 32) * 32;
    total_time +=
        predictions_.at(PredictionOps::ATTN_PREFILL)
            .at(GetPredictionKey(kv_cache_size, prefill_chunk_size_rounded));
  }

  return total_time;
}

double ExecutionTimePredictor::GetMlpLayerUpProjExecutionTime(
    const entities::Batch& batch) const
{
  return predictions_.at(PredictionOps::MLP_UP_PROJ)
      .at(GetPredictionKey(batch.total_num_q_tokens_rounded));
}

double ExecutionTimePredictor::GetMlpLayerDownProjExecutionTime(
    const entities::Batch& batch) const
{
  return predictions_.at(PredictionOps::MLP_DOWN_PROJ)
      .at(GetPredictionKey(batch.total_num_q_tokens_rounded));
}

double ExecutionTimePredictor::GetMlpLayerActExecutionTime(
    const entities::Batch& batch) const
{
  return predictions_.at(PredictionOps::MLP_ACT)
      .at(GetPredictionKey(batch.total_num_q_tokens_rounded));
}

double ExecutionTimePredictor::GetTensorParallelCommunicationTime(
    const entities::Batch& batch) const
{
  return (
      predictions_.at(PredictionOps::ALL_REDUCE)
          .at(GetPredictionKey(batch.total_num_q_tokens_rounded)) +
      config_.nccl_cpu_launch_overhead_ms +
      config_.nccl_cpu_skew_overhead_per_device_ms *
          std::pow(replica_config_.tensor_parallel_size, 1.25));
}

double ExecutionTimePredictor::GetPipelineParallelCommunicationTime(
    const entities::Batch& batch) const
{
  return predictions_.at(PredictionOps::SEND_RECV)
      .at(GetPredictionKey(batch.total_num_q_tokens_rounded));
}

double ExecutionTimePredictor::GetMlpNormLayerActExecutionTime(
    const entities::Batch& batch) const
{
  if (!model_config_.post_attn_norm)
  {
    return 0.0;
  }

  return predictions_.at(PredictionOps::POST_ATTENTION_LAYERNORM)
      .at(GetPredictionKey(batch.total_num_q_tokens_rounded));
}

double ExecutionTimePredictor::GetAttnNormLayerActExecutionTime(
    const entities::Batch& batch) const
{
  return predictions_.at(PredictionOps::INPUT_LAYERNORM)
      .at(GetPredictionKey(batch.total_num_q_tokens_rounded));
}

double ExecutionTimePredictor::GetAddLayerActExecutionTime(
    const entities::Batch& batch) const
{
  return predictions_.at(PredictionOps::ADD)
      .at(GetPredictionKey(batch.total_num_q_tokens_rounded));
}

double ExecutionTimePredictor::GetKvParallelCommunicationTime(
    const entities::Batch& batch) const
{
  if (!config_.disable_kvp_communication)
  {
    return 0.0;
  }

  double total_comm_time = 0.0;

  for (std::size_t i = 0; i < batch.num_requests; i++)
  {
    std::size_t num_q_tokens = batch.num_q_tokens[i];
    std::size_t num_groups = batch.num_active_kvp_groups[i];

    if (num_q_tokens == 0)
    {
      continue;
    }

    // round up to the nearest multiple of 8
    num_q_tokens = ((num_q_tokens + 7) / 8) * 8;

    total_comm_time +=
        (predictions_.at(PredictionOps::ALL_REDUCE_KVP)
             .at(GetPredictionKey(num_q_tokens, num_groups)) +
         config_.nccl_cpu_launch_overhead_ms +
         config_.nccl_cpu_skew_overhead_per_device_ms *
             std::pow(num_groups, 1.25));
  }

  return total_comm_time;
}

PredictionKey ExecutionTimePredictor::GetBatchDecodeAttentionParams(
    const entities::Batch& batch) const
{
  std::vector<std::size_t> decode_kv_cache_sizes;

  for (std::size_t i = 0; i < batch.num_requests; i++)
  {
    std::size_t num_q_tokens = batch.num_q_tokens[i];
    std::size_t num_kv_tokens = batch.num_kv_tokens[i];

    if (num_q_tokens != 1)
    {
      continue;
    }

    decode_kv_cache_sizes.push_back(num_kv_tokens);
  }

  if (decode_kv_cache_sizes.size() == 0)
  {
    return GetPredictionKey(0, 0);
  }

  std::size_t decode_batch_size = decode_kv_cache_sizes.size();
  std::size_t decode_avg_kv_cache_size = std::accumulate(
                                             decode_kv_cache_sizes.begin(),
                                             decode_kv_cache_sizes.end(),
                                             0) /
                                         decode_batch_size;

  decode_avg_kv_cache_size = ((decode_avg_kv_cache_size +
                               config_.kv_cache_prediction_granularity - 1) /
                              config_.kv_cache_prediction_granularity) *
                             config_.kv_cache_prediction_granularity;

  return GetPredictionKey(decode_batch_size, decode_avg_kv_cache_size);
}

std::vector<PredictionKey>
ExecutionTimePredictor::GetBatchPrefillAttentionParams(
    const entities::Batch& batch) const
{
  std::vector<PredictionKey> prefill_params;

  for (std::size_t i = 0; i < batch.num_requests; i++)
  {
    std::size_t num_q_tokens = batch.num_q_tokens[i];
    std::size_t num_kv_tokens = batch.num_kv_tokens[i];

    if (num_q_tokens == 1)
    {
      continue;
    }

    num_kv_tokens =
        ((num_kv_tokens + config_.kv_cache_prediction_granularity - 1) /
         config_.kv_cache_prediction_granularity) *
        config_.kv_cache_prediction_granularity;

    prefill_params.push_back(GetPredictionKey(num_kv_tokens, num_q_tokens));
  }

  return prefill_params;
}

} // namespace execution_time_predictor
} // namespace vidur