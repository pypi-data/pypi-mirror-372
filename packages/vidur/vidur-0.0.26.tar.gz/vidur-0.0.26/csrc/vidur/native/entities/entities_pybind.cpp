#include "vidur/entities/entities_pybind.h"

#include <pybind11/stl.h>

#include "vidur/entities/batch.h"
#include "vidur/entities/execution_time.h"
#include "vidur/entities/kv_parallel_batch.h"

namespace vidur
{
namespace entities
{
namespace py = pybind11;

void InitBatch(pybind11::module_& m)
{
  py::class_<Batch, std::shared_ptr<Batch>>(m, "Batch")
      .def(
          py::init<
              std::size_t,
              std::size_t,
              const std::vector<std::size_t>&,
              const std::vector<std::size_t>&,
              const std::vector<std::size_t>&,
              std::size_t>(),
          py::arg("replica_id"),
          py::arg("num_requests"),
          py::arg("num_q_tokens"),
          py::arg("num_kv_tokens"),
          py::arg("num_active_kvp_groups"),
          py::arg("kvp_group_id"))
      .def_readonly("replica_id", &Batch::replica_id)
      .def_readonly("num_requests", &Batch::num_requests)
      .def_readonly("num_q_tokens", &Batch::num_q_tokens)
      .def_readonly("num_kv_tokens", &Batch::num_kv_tokens)
      .def_readonly("num_active_kvp_groups", &Batch::num_active_kvp_groups)
      .def_readonly("kvp_group_id", &Batch::kvp_group_id)
      .def_readonly("total_num_q_tokens", &Batch::total_num_q_tokens)
      .def_readonly("total_num_kv_tokens", &Batch::total_num_kv_tokens)
      .def_readonly(
          "total_num_q_tokens_rounded",
          &Batch::total_num_q_tokens_rounded)
      .def("__str__", &Batch::ToString)
      .def("__repr__", &Batch::ToString);
}

void InitKVParallelBatch(pybind11::module_& m)
{
  py::class_<KVParallelBatch, std::shared_ptr<KVParallelBatch>>(
      m,
      "KVParallelBatch")
      .def(
          py::init<
              std::size_t,
              const std::vector<std::size_t>&,
              const std::vector<BatchPtr>&>(),
          py::arg("replica_id"),
          py::arg("kvp_group_ids"),
          py::arg("batches"))
      .def_readonly("replica_id", &KVParallelBatch::replica_id)
      .def_readonly("batch_mapping", &KVParallelBatch::batch_mapping)
      .def("__str__", &KVParallelBatch::ToString)
      .def("__repr__", &KVParallelBatch::ToString);
}

void InitExecutionTime(pybind11::module_& m)
{
  py::class_<ExecutionTime>(m, "ExecutionTime")
      .def(
          py::init<
              std::size_t,
              double,
              double,
              double,
              double,
              double,
              double,
              double,
              double,
              double,
              double,
              double,
              double,
              double,
              double>(),
          py::arg("num_layers_per_pipeline_stage"),
          py::arg("attention_rope_execution_time"),
          py::arg("attention_kv_cache_save_execution_time"),
          py::arg("attention_decode_execution_time"),
          py::arg("attention_prefill_execution_time"),
          py::arg("attention_layer_pre_proj_execution_time"),
          py::arg("attention_layer_post_proj_execution_time"),
          py::arg("mlp_layer_up_proj_execution_time"),
          py::arg("mlp_layer_down_proj_execution_time"),
          py::arg("mlp_layer_act_execution_time"),
          py::arg("attn_norm_time"),
          py::arg("mlp_norm_time"),
          py::arg("add_time"),
          py::arg("tensor_parallel_communication_time"),
          py::arg("pipeline_parallel_communication_time"))
      .def(
          "_get_mlp_layer_execution_time",
          &ExecutionTime::GetMlpLayerExecutionTime)
      .def(
          "_get_attention_layer_execution_time",
          &ExecutionTime::GetAttentionLayerExecutionTime)
      .def("_get_block_execution_time", &ExecutionTime::GetBlockExecutionTime)
      .def_property_readonly("model_time", &ExecutionTime::GetModelTime)
      .def_property_readonly("model_time_ms", &ExecutionTime::GetModelTimeMs)
      .def_property_readonly("total_time", &ExecutionTime::GetTotalTime)
      .def_readonly("num_layers", &ExecutionTime::num_layers)
      .def_readonly(
          "attention_rope_execution_time",
          &ExecutionTime::attention_rope_execution_time)
      .def_readonly(
          "attention_kv_cache_save_execution_time",
          &ExecutionTime::attention_kv_cache_save_execution_time)
      .def_readonly(
          "attention_decode_execution_time",
          &ExecutionTime::attention_decode_execution_time)
      .def_readonly(
          "attention_prefill_execution_time",
          &ExecutionTime::attention_prefill_execution_time)
      .def_readonly(
          "attention_layer_pre_proj_execution_time",
          &ExecutionTime::attention_layer_pre_proj_execution_time)
      .def_readonly(
          "attention_layer_post_proj_execution_time",
          &ExecutionTime::attention_layer_post_proj_execution_time)
      .def_readonly(
          "mlp_layer_up_proj_execution_time",
          &ExecutionTime::mlp_layer_up_proj_execution_time)
      .def_readonly(
          "mlp_layer_down_proj_execution_time",
          &ExecutionTime::mlp_layer_down_proj_execution_time)
      .def_readonly(
          "mlp_layer_act_execution_time",
          &ExecutionTime::mlp_layer_act_execution_time)
      .def_readonly("attn_norm_time", &ExecutionTime::attn_norm_time)
      .def_readonly("mlp_norm_time", &ExecutionTime::mlp_norm_time)
      .def_readonly("add_time", &ExecutionTime::add_time)
      .def_readonly(
          "tensor_parallel_communication_time",
          &ExecutionTime::tensor_parallel_communication_time)
      .def_readonly(
          "pipeline_parallel_communication_time",
          &ExecutionTime::pipeline_parallel_communication_time)
      .def("__str__", &ExecutionTime::ToString)
      .def("__repr__", &ExecutionTime::ToString);
}

} // namespace entities
} // namespace vidur
