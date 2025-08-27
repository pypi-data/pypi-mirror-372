#pragma once
#include <memory>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

namespace vidur
{
namespace entities
{

struct Batch final
{
  Batch(
      std::size_t replica_id,
      std::size_t num_requests,
      const std::vector<std::size_t>& num_q_tokens,
      const std::vector<std::size_t>& num_kv_tokens,
      const std::vector<std::size_t>& num_active_kvp_groups,
      std::size_t kvp_group_id);

  [[nodiscard]] std::string ToString() const;

  // Members
  const std::size_t replica_id;
  const std::size_t num_requests;
  const std::vector<std::size_t> num_q_tokens;
  const std::vector<std::size_t> num_kv_tokens;
  const std::vector<std::size_t> num_active_kvp_groups;
  const std::size_t kvp_group_id;
  const std::size_t total_num_q_tokens;
  const std::size_t total_num_kv_tokens;
  const std::size_t total_num_q_tokens_rounded;
};

} // namespace entities
} // namespace vidur