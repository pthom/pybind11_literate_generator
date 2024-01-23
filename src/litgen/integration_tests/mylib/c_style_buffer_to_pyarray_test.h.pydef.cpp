// ============================================================================
// This file was autogenerated
// It is presented side to side with its source: c_style_buffer_to_pyarray_test.h
// It is not used in the compilation
//    (see integration_tests/bindings/pybind_mylib.cpp which contains the full binding
//     code, including this code)
// ============================================================================

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/numpy.h>
#include "mylib/mylib_main/mylib.h"

namespace py = pybind11;

// <litgen_glue_code>  // Autogenerated code below! Do not edit!

// </litgen_glue_code> // Autogenerated code end


void py_init_module_mylib(py::module& m)
{
    // <litgen_pydef> // Autogenerated code below! Do not edit!
    ////////////////////    <generated_from:c_style_buffer_to_pyarray_test.h>    ////////////////////
    m.def("add_inside_buffer",
        [](py::array & buffer, uint8_t number_to_add)
        {
            auto add_inside_buffer_adapt_c_buffers = [](py::array & buffer, uint8_t number_to_add)
            {
                // convert py::array to C standard buffer (mutable)
                void * buffer_from_pyarray = buffer.mutable_data();
                py::ssize_t buffer_count = buffer.shape()[0];
                char buffer_type = buffer.dtype().char_();
                if (buffer_type != 'B')
                    throw std::runtime_error(std::string(R"msg(
                            Bad type!  Expected a numpy array of native type:
                                        uint8_t *
                                    Which is equivalent to
                                        B
                                    (using py::array::dtype().char_() as an id)
                        )msg"));

                add_inside_buffer(static_cast<uint8_t *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), number_to_add);
            };

            add_inside_buffer_adapt_c_buffers(buffer, number_to_add);
        },
        py::arg("buffer"), py::arg("number_to_add"),
        " add_inside_buffer: modifies a buffer by adding a value to its elements\n Will be published in python as:\n -->    def add_inside_buffer(buffer: np.ndarray, number_to_add: int) -> None:\n Warning, the python function will accept only uint8 numpy arrays, and check it at runtime!");

    m.def("buffer_sum",
        [](const py::array & buffer, int stride = -1) -> int
        {
            auto buffer_sum_adapt_c_buffers = [](const py::array & buffer, int stride = -1) -> int
            {
                // convert py::array to C standard buffer (const)
                const void * buffer_from_pyarray = buffer.data();
                py::ssize_t buffer_count = buffer.shape()[0];
                char buffer_type = buffer.dtype().char_();
                if (buffer_type != 'B')
                    throw std::runtime_error(std::string(R"msg(
                            Bad type!  Expected a numpy array of native type:
                                        const uint8_t *
                                    Which is equivalent to
                                        B
                                    (using py::array::dtype().char_() as an id)
                        )msg"));

                // process stride default value (which was a sizeof in C++)
                int buffer_stride = stride;
                if (buffer_stride == -1)
                    buffer_stride = (int)buffer.itemsize();

                auto lambda_result = buffer_sum(static_cast<const uint8_t *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), static_cast<size_t>(buffer_stride));
                return lambda_result;
            };

            return buffer_sum_adapt_c_buffers(buffer, stride);
        },
        py::arg("buffer"), py::arg("stride") = -1,
        " buffer_sum: returns the sum of a *const* buffer\n Will be published in python as:\n -->    def buffer_sum(buffer: np.ndarray, stride: int = -1) -> int:");

    m.def("add_inside_two_buffers",
        [](py::array & buffer_1, py::array & buffer_2, uint8_t number_to_add)
        {
            auto add_inside_two_buffers_adapt_c_buffers = [](py::array & buffer_1, py::array & buffer_2, uint8_t number_to_add)
            {
                // convert py::array to C standard buffer (mutable)
                void * buffer_1_from_pyarray = buffer_1.mutable_data();
                py::ssize_t buffer_1_count = buffer_1.shape()[0];
                char buffer_1_type = buffer_1.dtype().char_();
                if (buffer_1_type != 'B')
                    throw std::runtime_error(std::string(R"msg(
                            Bad type!  Expected a numpy array of native type:
                                        uint8_t *
                                    Which is equivalent to
                                        B
                                    (using py::array::dtype().char_() as an id)
                        )msg"));

                // convert py::array to C standard buffer (mutable)
                void * buffer_2_from_pyarray = buffer_2.mutable_data();
                py::ssize_t buffer_2_count = buffer_2.shape()[0];
                char buffer_2_type = buffer_2.dtype().char_();
                if (buffer_2_type != 'B')
                    throw std::runtime_error(std::string(R"msg(
                            Bad type!  Expected a numpy array of native type:
                                        uint8_t *
                                    Which is equivalent to
                                        B
                                    (using py::array::dtype().char_() as an id)
                        )msg"));

                add_inside_two_buffers(static_cast<uint8_t *>(buffer_1_from_pyarray), static_cast<uint8_t *>(buffer_2_from_pyarray), static_cast<size_t>(buffer_2_count), number_to_add);
            };

            add_inside_two_buffers_adapt_c_buffers(buffer_1, buffer_2, number_to_add);
        },
        py::arg("buffer_1"), py::arg("buffer_2"), py::arg("number_to_add"),
        " add_inside_two_buffers: modifies two mutable buffers\n litgen will detect that this function uses two buffers of same size.\n Will be published in python as:\n -->    def add_inside_two_buffers(buffer_1: np.ndarray, buffer_2: np.ndarray, number_to_add: int) -> None:");

    m.def("templated_mul_inside_buffer",
        [](py::array & buffer, double factor)
        {
            auto templated_mul_inside_buffer_adapt_c_buffers = [](py::array & buffer, double factor)
            {
                // convert py::array to C standard buffer (mutable)
                void * buffer_from_pyarray = buffer.mutable_data();
                py::ssize_t buffer_count = buffer.shape()[0];

                #ifdef _WIN32
                using np_uint_l = uint32_t;
                using np_int_l = int32_t;
                #else
                using np_uint_l = uint64_t;
                using np_int_l = int64_t;
                #endif
                // call the correct template version by casting
                char buffer_type = buffer.dtype().char_();
                if (buffer_type == 'B')
                    templated_mul_inside_buffer(static_cast<uint8_t *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), factor);
                else if (buffer_type == 'b')
                    templated_mul_inside_buffer(static_cast<int8_t *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), factor);
                else if (buffer_type == 'H')
                    templated_mul_inside_buffer(static_cast<uint16_t *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), factor);
                else if (buffer_type == 'h')
                    templated_mul_inside_buffer(static_cast<int16_t *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), factor);
                else if (buffer_type == 'I')
                    templated_mul_inside_buffer(static_cast<uint32_t *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), factor);
                else if (buffer_type == 'i')
                    templated_mul_inside_buffer(static_cast<int32_t *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), factor);
                else if (buffer_type == 'L')
                    templated_mul_inside_buffer(static_cast<np_uint_l *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), factor);
                else if (buffer_type == 'l')
                    templated_mul_inside_buffer(static_cast<np_int_l *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), factor);
                else if (buffer_type == 'f')
                    templated_mul_inside_buffer(static_cast<float *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), factor);
                else if (buffer_type == 'd')
                    templated_mul_inside_buffer(static_cast<double *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), factor);
                else if (buffer_type == 'g')
                    templated_mul_inside_buffer(static_cast<long double *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), factor);
                else if (buffer_type == 'q')
                    templated_mul_inside_buffer(static_cast<long long *>(buffer_from_pyarray), static_cast<size_t>(buffer_count), factor);
                // If we reach this point, the array type is not supported!
                else
                    throw std::runtime_error(std::string("Bad array type ('") + buffer_type + "') for param buffer");
            };

            templated_mul_inside_buffer_adapt_c_buffers(buffer, factor);
        },
        py::arg("buffer"), py::arg("factor"),
        " templated_mul_inside_buffer: template function that modifies an array by multiplying its elements by a given factor\n litgen will detect that this function can be published as using a numpy array.\n It will be published in python as:\n -->    def mul_inside_buffer(buffer: np.ndarray, factor: float) -> None:\n\n The type will be detected at runtime and the correct template version will be called accordingly!\n An error will be thrown if the numpy array numeric type is not supported.");
    ////////////////////    </generated_from:c_style_buffer_to_pyarray_test.h>    ////////////////////

    // </litgen_pydef> // Autogenerated code end
}