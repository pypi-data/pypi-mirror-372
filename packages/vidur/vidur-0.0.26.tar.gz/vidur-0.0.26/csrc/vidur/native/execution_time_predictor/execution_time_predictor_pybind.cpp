#include "vidur/execution_time_predictor/execution_time_predictor_pybind.h"

#include "vidur/execution_time_predictor/execution_time_predictor.h"
#include <pybind11/stl.h>

namespace vidur
{
namespace execution_time_predictor
{

namespace py = pybind11;

void InitExecutionTimePredictor(pybind11::module_& m)
{
  py::class_<ExecutionTimePredictor, std::shared_ptr<ExecutionTimePredictor>>(
      m,
      "ExecutionTimePredictor")
      .def(
          py::init<
              const config::ExecutionTimePredictorConfig&,
              const config::ReplicaConfig&,
              const config::ModelConfig&,
              const std::vector<std::string>&,
              const std::vector<std::vector<PredictionKey>>&,
              const std::vector<std::vector<double>>&,
              const std::string&>(),
          py::arg("config"),
          py::arg("replica_config"),
          py::arg("model_config"),
          py::arg("prediction_ops"),
          py::arg("prediction_keys"),
          py::arg("prediction_values"),
          py::arg("hash"))
      .def(
          "get_execution_time_batch",
          &ExecutionTimePredictor::GetExecutionTimeBatch,
          py::arg("batch"),
          py::arg("pipeline_stage"))
      .def(
          "get_execution_time_kv_parallel_batch",
          &ExecutionTimePredictor::GetExecutionTimeKVParallelBatch,
          py::arg("kvp_batch"),
          py::arg("pipeline_stage"))
      .def("get_hash", &ExecutionTimePredictor::GetHash)
      .def(
          "as_capsule",
          [](std::shared_ptr<ExecutionTimePredictor> self)
          {
            auto* sp_copy =
                new std::shared_ptr<const ExecutionTimePredictor>(self);
            return py::capsule(
                sp_copy,
                "ExecutionTimePredictorPtr",
                [](PyObject* capsule)
                {
                  auto* raw = static_cast<
                      std::shared_ptr<const ExecutionTimePredictor>*>(
                      PyCapsule_GetPointer(
                          capsule,
                          "ExecutionTimePredictorPtr"));
                  delete raw; // Freed when capsule is GC'd
                });
          });
}

} // namespace execution_time_predictor
} // namespace vidur
