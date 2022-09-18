#include "inner_classes.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>

namespace py = pybind11;

void py_init_module_hello_imgui(py::module& m)
{
    //using namespace Main;
    //using namespace Main::Inner;

    // <litgen_pydef> // Autogenerated code below! Do not edit!
    ////////////////////    <generated_from:submodules.h>    ////////////////////
    // <namespace Main>
    auto pyClassA = py::class_<A>
        (m, "A", "")
        .def(py::init<>()) // implicit default constructor
        .def_readwrite("a", &A::a, "")
        ;
    // </namespace Main>
    ////////////////////    </generated_from:submodules.h>    ////////////////////

    // </litgen_pydef> //
}