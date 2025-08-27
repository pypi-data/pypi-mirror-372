#include "vidur/entities/kv_parallel_batch.h"

#include <fmt/core.h>

namespace vidur
{
namespace entities
{

KVParallelBatch::KVParallelBatch(
    std::size_t replica_id,
    const std::vector<std::size_t>& kvp_group_ids,
    const std::vector<BatchPtr>& batches)
    : replica_id(replica_id)
{
  batch_mapping.reserve(kvp_group_ids.size());
  for (std::size_t i = 0; i < kvp_group_ids.size(); ++i)
  {
    batch_mapping[kvp_group_ids[i]] = batches[i];
  }
}

std::string KVParallelBatch::ToString() const
{
  std::string result =
      fmt::format("KVParallelBatch(replica_id={}, batches=[", replica_id);
  bool first = true;
  for (const auto& [kvp_group_id, batch] : batch_mapping)
  {
    if (!first)
      result += ", ";
    result += fmt::format(
        "{{kvp_group_id={}, batch={}}}",
        kvp_group_id,
        batch->ToString());
    first = false;
  }
  result += "])";
  return result;
}

} // namespace entities
} // namespace vidur
