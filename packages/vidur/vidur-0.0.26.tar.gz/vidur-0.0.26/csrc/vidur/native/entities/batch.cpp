#include "vidur/entities/batch.h"

#include <algorithm>
#include <fmt/core.h>
#include <fmt/ranges.h>

namespace vidur
{
namespace entities
{

Batch::Batch(
    std::size_t replica_id,
    std::size_t num_requests,
    const std::vector<std::size_t>& num_q_tokens,
    const std::vector<std::size_t>& num_kv_tokens,
    const std::vector<std::size_t>& num_active_kvp_groups,
    std::size_t kvp_group_id)
    : replica_id(replica_id),
      num_requests(num_requests),
      num_q_tokens(num_q_tokens),
      num_kv_tokens(num_kv_tokens),
      num_active_kvp_groups(num_active_kvp_groups),
      kvp_group_id(kvp_group_id),
      total_num_q_tokens(
          std::accumulate(num_q_tokens.begin(), num_q_tokens.end(), 0)),
      total_num_kv_tokens(
          std::accumulate(num_kv_tokens.begin(), num_kv_tokens.end(), 0)),
      total_num_q_tokens_rounded(((total_num_q_tokens + 7) / 8) * 8)
{
}

std::string Batch::ToString() const
{
  return fmt::format(
      "Batch(replica_id={}, num_requests={}, num_q_tokens={}, "
      "num_kv_tokens={}, num_active_kvp_groups={}, kvp_group_id={})",
      replica_id,
      num_requests,
      fmt::format("[{}]", fmt::join(num_q_tokens, ",")),
      fmt::format("[{}]", fmt::join(num_kv_tokens, ",")),
      fmt::format("[{}]", fmt::join(num_active_kvp_groups, ",")),
      kvp_group_id);
}

} // namespace entities
} // namespace vidur
