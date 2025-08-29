// bindings/binding.cpp
#include <pybind11/pybind11.h>
#include "../flood_solver.h"

namespace py = pybind11;

PYBIND11_MODULE(flood, m) {
    m.doc() = R"pbdoc(
        flood Simulation Engine
        ===========================

        A simplified 2D flood diffusion model with GPU acceleration.
    )pbdoc";

    m.def("run", &run_simulation, R"pbdoc(
        run(work_dir)

        Run a simplified flood simulation.

        Parameters:
            work_dir (str): Path to the case directory.

        Returns:
            int: 0 for success.
    )pbdoc");
}
