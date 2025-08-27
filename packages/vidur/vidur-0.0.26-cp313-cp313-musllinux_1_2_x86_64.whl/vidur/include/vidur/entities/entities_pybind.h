#pragma once
#include <pybind11/pybind11.h>

namespace vidur
{
namespace entities
{

void InitBatch(pybind11::module_&);
void InitKVParallelBatch(pybind11::module_&);
void InitExecutionTime(pybind11::module_&);

} // namespace entities

inline void InitEntities(pybind11::module_& m)
{
  auto entities_module = m.def_submodule("entities");
  entities::InitBatch(entities_module);
  entities::InitKVParallelBatch(entities_module);
  entities::InitExecutionTime(entities_module);
}

} // namespace vidur
