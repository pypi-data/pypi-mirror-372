#pragma once

#include <pybind11/pybind11.h>

namespace vidur
{
namespace config
{

void InitExecutionTimePredictorConfig(pybind11::module_&);
void InitModelConfig(pybind11::module_&);
void InitReplicaConfig(pybind11::module_&);
void InitCacheConfig(pybind11::module_&);

} // namespace config

inline void InitConfig(pybind11::module_& m)
{
  auto config_module = m.def_submodule("config");
  config::InitExecutionTimePredictorConfig(config_module);
  config::InitModelConfig(config_module);
  config::InitReplicaConfig(config_module);
  config::InitCacheConfig(config_module);
}

} // namespace vidur
