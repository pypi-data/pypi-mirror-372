#pragma once
#include <string>

namespace vidur
{
namespace execution_time_predictor
{

struct PredictionOps
{
  // Attention related keys
  static inline const std::string ATTN_PRE_PROJ = "attn_pre_proj";
  static inline const std::string ATTN_POST_PROJ = "attn_post_proj";
  static inline const std::string ATTN_ROPE = "attn_rope";
  static inline const std::string ATTN_KV_CACHE_SAVE = "attn_kv_cache_save";
  static inline const std::string ATTN_DECODE = "attn_decode";
  static inline const std::string ATTN_PREFILL = "attn_prefill";

  // MLP related keys
  static inline const std::string MLP_UP_PROJ = "mlp_up_proj";
  static inline const std::string MLP_DOWN_PROJ = "mlp_down_proj";
  static inline const std::string MLP_ACT = "mlp_act";

  // Communication related keys
  static inline const std::string ALL_REDUCE = "all_reduce";
  static inline const std::string SEND_RECV = "send_recv";
  static inline const std::string ALL_REDUCE_KVP = "all_reduce_kvp";

  // Layer norm and other keys
  static inline const std::string POST_ATTENTION_LAYERNORM =
      "post_attention_layernorm";
  static inline const std::string INPUT_LAYERNORM = "input_layernorm";
  static inline const std::string ADD = "add";
};

} // namespace execution_time_predictor
} // namespace vidur
