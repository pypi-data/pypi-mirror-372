#include <pybind11/pybind11.h>

#include "vidur/config/config_pybind.h"
#include "vidur/entities/entities_pybind.h"
#include "vidur/execution_time_predictor/execution_time_predictor_pybind.h"

PYBIND11_MODULE(_native, m)
{
  m.doc() = "Vidur native C++ bindings";
  vidur::InitEntities(m);
  vidur::InitExecutionTimePredictor(m);
  vidur::InitConfig(m);
}
