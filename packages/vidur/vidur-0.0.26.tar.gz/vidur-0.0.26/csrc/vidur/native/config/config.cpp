#include "vidur/config/config.h"

namespace vidur
{
namespace config
{

ExecutionTimePredictorConfig::ExecutionTimePredictorConfig(
    std::size_t kv_cache_prediction_granularity,
    std::size_t prediction_max_prefill_chunk_size,
    std::size_t prediction_max_batch_size,
    std::size_t prediction_max_tokens_per_request,
    double attention_decode_batching_overhead_fraction,
    double nccl_cpu_launch_overhead_ms,
    double nccl_cpu_skew_overhead_per_device_ms,
    bool use_native_execution_time_predictor,
    bool disable_kvp_communication,
    std::string cache_dir)
    : kv_cache_prediction_granularity(kv_cache_prediction_granularity),
      prediction_max_prefill_chunk_size(prediction_max_prefill_chunk_size),
      prediction_max_batch_size(prediction_max_batch_size),
      prediction_max_tokens_per_request(prediction_max_tokens_per_request),
      attention_decode_batching_overhead_fraction(
          attention_decode_batching_overhead_fraction),
      nccl_cpu_launch_overhead_ms(nccl_cpu_launch_overhead_ms),
      nccl_cpu_skew_overhead_per_device_ms(
          nccl_cpu_skew_overhead_per_device_ms),
      use_native_execution_time_predictor(use_native_execution_time_predictor),
      disable_kvp_communication(disable_kvp_communication),
      cache_dir(cache_dir)
{
}

ReplicaConfig::ReplicaConfig(
    std::size_t num_pipeline_stages,
    std::size_t tensor_parallel_size,
    std::size_t kv_parallel_size)
    : num_pipeline_stages(num_pipeline_stages),
      tensor_parallel_size(tensor_parallel_size),
      kv_parallel_size(kv_parallel_size)
{
}

ModelConfig::ModelConfig(
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
    std::size_t vocab_size)
    : num_layers(num_layers),
      num_q_heads(num_q_heads),
      num_kv_heads(num_kv_heads),
      embedding_dim(embedding_dim),
      mlp_hidden_dim(mlp_hidden_dim),
      max_model_len(max_model_len),
      use_gated_mlp(use_gated_mlp),
      use_bias(use_bias),
      use_qkv_bias(use_qkv_bias),
      post_attn_norm(post_attn_norm),
      vocab_size(vocab_size)
{
}

CacheConfig::CacheConfig(
    std::size_t block_size,
    std::size_t num_blocks,
    double watermark_blocks_fraction,
    double memory_margin_fraction,
    bool enable_prefix_caching,
    std::string prefix_caching_hash_algo,
    std::size_t num_preallocate_tokens,
    bool enable_disk_caching,
    std::size_t disk_num_blocks)
    : block_size(block_size),
      num_blocks(num_blocks),
      watermark_blocks_fraction(watermark_blocks_fraction),
      memory_margin_fraction(memory_margin_fraction),
      enable_prefix_caching(enable_prefix_caching),
      prefix_caching_hash_algo(prefix_caching_hash_algo),
      num_preallocate_tokens(num_preallocate_tokens),
      enable_disk_caching(enable_disk_caching),
      disk_num_blocks(disk_num_blocks)
{
}

} // namespace config
} // namespace vidur
