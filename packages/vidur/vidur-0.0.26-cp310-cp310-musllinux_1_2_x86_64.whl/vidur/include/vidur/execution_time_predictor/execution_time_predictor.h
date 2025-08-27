#pragma once
#include <memory>
#include <numeric>
#include <unordered_map>
#include <utility>

#include "vidur/config/config.h"
#include "vidur/entities/batch.h"
#include "vidur/entities/execution_time.h"
#include "vidur/entities/kv_parallel_batch.h"
#include "vidur/execution_time_predictor/prediction_keys.h"

namespace vidur
{
namespace execution_time_predictor
{
struct PairHash
{
  template <class T1, class T2>
  [[nodiscard]] std::size_t operator()(const std::pair<T1, T2>& pair) const
  {
    auto h1 = std::hash<T1>{}(pair.first);
    auto h2 = std::hash<T2>{}(pair.second);
    return h1 ^ (h2 << 1);
  }
};

using PredictionKey = std::pair<int, int>;
using PredictionMap = std::unordered_map<
    std::string,
    std::unordered_map<PredictionKey, double, PairHash>>;

class ExecutionTimePredictor
{
public:
  static inline PredictionKey GetPredictionKey(int x)
  {
    return std::make_pair(x, -1);
  }
  static inline PredictionKey GetPredictionKey(int x, int y)
  {
    return std::make_pair(x, y);
  }

  ExecutionTimePredictor(
      const config::ExecutionTimePredictorConfig config,
      const config::ReplicaConfig replica_config,
      const config::ModelConfig model_config,
      const std::vector<std::string>& prediction_ops,
      const std::vector<std::vector<PredictionKey>>& prediction_keys,
      const std::vector<std::vector<double>>& prediction_values,
      const std::string& hash);

  // Main prediction method
  [[nodiscard]] entities::ExecutionTime GetExecutionTimeBatch(
      const entities::Batch& batch,
      std::size_t pipeline_stage) const;

  [[nodiscard]] entities::ExecutionTime GetExecutionTimeKVParallelBatch(
      const entities::KVParallelBatch& kvp_batch,
      std::size_t pipeline_stage) const;

  [[nodiscard]] std::string GetHash() const { return hash_; }

  [[nodiscard]] std::string GetCacheDir() const { return config_.cache_dir; }

private:
  // Helper methods for timing predictions
  double
  GetAttentionLayerPreProjExecutionTime(const entities::Batch& batch) const;
  double
  GetAttentionLayerPostProjExecutionTime(const entities::Batch& batch) const;
  double GetAttentionRopeExecutionTime(const entities::Batch& batch) const;
  double
  GetAttentionKvCacheSaveExecutionTime(const entities::Batch& batch) const;
  double GetAttentionDecodeExecutionTime(const entities::Batch& batch) const;
  double GetAttentionPrefillExecutionTime(const entities::Batch& batch) const;
  double GetMlpLayerUpProjExecutionTime(const entities::Batch& batch) const;
  double GetMlpLayerDownProjExecutionTime(const entities::Batch& batch) const;
  double GetMlpLayerActExecutionTime(const entities::Batch& batch) const;
  double GetTensorParallelCommunicationTime(const entities::Batch& batch) const;
  double
  GetPipelineParallelCommunicationTime(const entities::Batch& batch) const;
  double GetMlpNormLayerActExecutionTime(const entities::Batch& batch) const;
  double GetAttnNormLayerActExecutionTime(const entities::Batch& batch) const;
  double GetAddLayerActExecutionTime(const entities::Batch& batch) const;
  double GetKvParallelCommunicationTime(const entities::Batch& batch) const;
  PredictionKey
  GetBatchDecodeAttentionParams(const entities::Batch& batch) const;
  std::vector<PredictionKey>
  GetBatchPrefillAttentionParams(const entities::Batch& batch) const;

  const config::ExecutionTimePredictorConfig config_;
  const config::ReplicaConfig replica_config_;
  const config::ModelConfig model_config_;
  const std::string hash_;
  const std::size_t num_layers_per_pipeline_stage_;

  PredictionMap predictions_;
};

} // namespace execution_time_predictor
} // namespace vidur
