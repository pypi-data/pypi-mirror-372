#pragma once
#include <memory>
#include <unordered_map>

#include "vidur/entities/batch.h"

namespace vidur
{
namespace entities
{
using BatchPtr = std::shared_ptr<const Batch>;
using BatchMap = std::unordered_map<std::size_t, BatchPtr>;

struct KVParallelBatch final
{
  KVParallelBatch(
      std::size_t replica_id,
      const std::vector<std::size_t>& kvp_group_ids,
      const std::vector<BatchPtr>& batches);

  [[nodiscard]] std::string ToString() const;

  // Members
  const std::size_t replica_id;
  BatchMap batch_mapping;
};

} // namespace entities
} // namespace vidur
