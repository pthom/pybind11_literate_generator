#include "basic.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>

namespace py = pybind11;

void py_init_module_hello_imgui(py::module& m)
{
    using namespace Basic;

    // <litgen_pydef> // Autogenerated code below! Do not edit!
    ////////////////////    <generated_from:basic.h>    ////////////////////
    // <namespace Basic>
    m.def("add",
        add, py::arg("a"), py::arg("b"));
    // </namespace Basic>
    ////////////////////    </generated_from:basic.h>    ////////////////////

    // </litgen_pydef> //
}
