#pragma once
#include <pybind11/pybind11.h>

namespace vidur
{
namespace execution_time_predictor
{

void InitExecutionTimePredictor(pybind11::module_&);

} // namespace execution_time_predictor

inline void InitExecutionTimePredictor(pybind11::module_& m)
{
  auto predictor_module = m.def_submodule("execution_time_predictor");
  execution_time_predictor::InitExecutionTimePredictor(predictor_module);
}

} // namespace vidur
