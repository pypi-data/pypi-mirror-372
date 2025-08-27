#pragma once
#include <cstddef>
#include <limits>
#include <string>

namespace vidur
{
namespace config
{

struct ExecutionTimePredictorConfig final
{
  ExecutionTimePredictorConfig(
      std::size_t kv_cache_prediction_granularity = 256,
      std::size_t prediction_max_prefill_chunk_size = 4096,
      std::size_t prediction_max_batch_size = 128,
      std::size_t prediction_max_tokens_per_request = 2 * 1024 * 1024,
      double attention_decode_batching_overhead_fraction = 0.1,
      double nccl_cpu_launch_overhead_ms = 0.02,
      double nccl_cpu_skew_overhead_per_device_ms = 0.0,
      bool use_native_execution_time_predictor = true,
      bool disable_kvp_communication = true,
      std::string cache_dir = ".vidur_cache");

  // Members
  const std::size_t kv_cache_prediction_granularity;
  const std::size_t prediction_max_prefill_chunk_size;
  const std::size_t prediction_max_batch_size;
  const std::size_t prediction_max_tokens_per_request;
  const double attention_decode_batching_overhead_fraction;
  const double nccl_cpu_launch_overhead_ms;
  const double nccl_cpu_skew_overhead_per_device_ms;
  const bool use_native_execution_time_predictor;
  const bool disable_kvp_communication;
  const std::string cache_dir;
};

struct ReplicaConfig final
{
  ReplicaConfig(
      std::size_t num_pipeline_stages,
      std::size_t tensor_parallel_size,
      std::size_t kv_parallel_size);

  // Members
  const std::size_t num_pipeline_stages;
  const std::size_t tensor_parallel_size;
  const std::size_t kv_parallel_size;
};

struct ModelConfig final
{
  ModelConfig(
      std::size_t num_layers,
      std::size_t num_q_heads,
      std::size_t num_kv_heads,
      std::size_t embedding_dim,
      std::size_t mlp_hidden_dim,
      std::size_t max_model_len,
      bool use_gated_mlp,
      bool use_bias,
      bool use_qkv_bias,
      bool post_attn_norm,
      std::size_t vocab_size);

  // Members
  const std::size_t num_layers;
  const std::size_t num_q_heads;
  const std::size_t num_kv_heads;
  const std::size_t embedding_dim;
  const std::size_t mlp_hidden_dim;
  const std::size_t max_model_len;
  const bool use_gated_mlp;
  const bool use_bias;
  const bool use_qkv_bias;
  const bool post_attn_norm;
  const std::size_t vocab_size;
};

struct CacheConfig final
{
  CacheConfig(
      std::size_t block_size = 16,
      std::size_t num_blocks = 0,
      double watermark_blocks_fraction = 0.01,
      double memory_margin_fraction = 0.1,
      bool enable_prefix_caching = false,
      std::string prefix_caching_hash_algo = "builtin",
      std::size_t num_preallocate_tokens = 64,
      bool enable_disk_caching = false,
      std::size_t disk_num_blocks = std::numeric_limits<std::size_t>::max());

  // Members
  const std::size_t block_size;
  const std::size_t num_blocks;
  const double watermark_blocks_fraction;
  const double memory_margin_fraction;
  const bool enable_prefix_caching;
  const std::string prefix_caching_hash_algo;
  const std::size_t num_preallocate_tokens;
  const bool enable_disk_caching;
  const std::size_t disk_num_blocks;
};

} // namespace config
} // namespace vidur
