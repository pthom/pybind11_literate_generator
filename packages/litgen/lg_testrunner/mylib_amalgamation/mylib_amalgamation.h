// THIS FILE WAS GENERATED AUTOMATICALLY. DO NOT EDIT.

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       mylib/mylib.h                                                                          //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <cstddef>
#include <cstring>
#include <stdint.h>
#include <stdio.h>
#include <string>
#include <memory>
#include <vector>
#include <array>


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       mylib/api_marker.h included by mylib/mylib.h                                           //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#ifndef MY_API
#define MY_API  // MY_API could typically be __declspec(dllexport | dllimport)
#endif

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       mylib/header_filter_test.h included by mylib/mylib.h                                   //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Here, we test that functions placed under unknown preprocessor defines are not exported by default
// You could choose to add them anyway with:
// ````
//    options.srcml_options.header_guard_suffixes.append("OBSCURE_OPTION")
// ````

#ifdef OBSCURE_OPTION
MY_API int ObscureFunction() { return 42; }
#endif

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       mylib/c_style_array_test.h included by mylib/mylib.h                                   //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//
// C Style array tests
//

// Tests with Boxed Numbers
MY_API inline int add_c_array2(const int values[2]) { return values[0] + values[1];}
MY_API inline void log_c_array2(const int values[2]) { printf("%i, %i\n", values[0], values[1]); }
MY_API inline void change_c_array2(unsigned long values[2])
{
    values[0] = values[1] + values[0];
    values[1] = values[0] * values[1];
}
// Test with C array containing user defined struct (which will not be boxed)
struct Point2 // MY_API
{
    int x, y;
};
MY_API inline void GetPoints(Point2 out[2]) { out[0] = {0, 1}; out[1] = {2, 3}; }

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       mylib/c_style_buffer_to_pyarray_test.h included by mylib/mylib.h                       //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//
// C Style buffer to py::array tests
//

// Modifies a buffer by adding a value to its elements
MY_API inline void add_inside_buffer(uint8_t* buffer, size_t buffer_size, uint8_t number_to_add)
{
    for (size_t i  = 0; i < buffer_size; ++i)
        buffer[i] += number_to_add;
}

// Returns the sum of a const buffer
MY_API inline int buffer_sum(const uint8_t* buffer, size_t buffer_size, size_t stride= sizeof(uint8_t))
{
    int sum = 0;
    for (size_t i  = 0; i < buffer_size; ++i)
        sum += (int)buffer[i];
    return sum;
}

// Modifies two buffers
MY_API inline void add_inside_two_buffers(uint8_t* buffer_1, uint8_t* buffer_2, size_t buffer_size, uint8_t number_to_add)
{
    for (size_t i  = 0; i < buffer_size; ++i)
    {
        buffer_1[i] += number_to_add;
        buffer_2[i] += number_to_add;
    }
}

// Modify an array by multiplying its elements (template function!)
template<typename T> MY_API void mul_inside_buffer(T* buffer, size_t buffer_size, double factor)
{
    for (size_t i  = 0; i < buffer_size; ++i)
        buffer[i] *= (T)factor;
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       mylib/c_string_list_test.h included by mylib/mylib.h                                   //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//
// C String lists tests
//

MY_API inline size_t c_string_list_total_size(const char * const items[], int items_count, int output[2])
{
    size_t total = 0;
    for (size_t i = 0; i < items_count; ++i)
        total += strlen(items[i]);
    output[0] = (int)total;
    output[1] = (int)(total + 1);
    return total;
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       mylib/modifiable_immutable_test.h included by mylib/mylib.h                            //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//
// Modifiable immutable python types test
//

/////////////////////////////////////////////////////////////////////////////////////////////
// Test Part 1: in the functions below, the value parameters will be "Boxed"
//
// This is caused by the following options during generation:
//     options.fn_params_replace_modifiable_immutable_by_boxed__regexes = [
//         r"^Toggle",
//         r"^Modify",
//      ]
/////////////////////////////////////////////////////////////////////////////////////////////


// Test with pointer
// -->    def toggle_bool_pointer(v: BoxedBool) -> None:
MY_API void ToggleBoolPointer(bool *v)
{
    *v = !(*v);
}

// Test with nullable pointer
// -->    def toggle_bool_nullable(v: BoxedBool = None) -> None:
MY_API void ToggleBoolNullable(bool *v = NULL)
{
    if (v != NULL)
        *v = !(*v);
}

// Test with reference
// -->    def toggle_bool_reference(v: BoxedBool) -> None:
MY_API void ToggleBoolReference(bool &v)
{
    v = !(v);
}

// Test modifiable String
// -->    def modify_string(s: BoxedString) -> None:
MY_API void ModifyString(std::string* s) { (*s) += "hello"; }


/////////////////////////////////////////////////////////////////////////////////////////////
//
// Test Part 2: in the functions below, the python return type is modified:
// the python functions will return a tuple:
//     (original_return_value, modified_parameter)
//
// This is caused by the following options during generation:
//
//     options.fn_params_output_modifiable_immutable_to_return__regexes = [r"^Slider"]
/////////////////////////////////////////////////////////////////////////////////////////////


// Test with int param + int return type
// --> def slider_bool_int(label: str, value: int) -> Tuple[bool, int]:
MY_API bool SliderBoolInt(const char* label, int * value)
{
    *value += 1;
    return true;
}

// -->    def slider_void_int(label: str, value: int) -> int:
MY_API void SliderVoidInt(const char* label, int * value)
{
    *value += 1;
}

// -->    def slider_bool_int2(label: str, value1: int, value2: int) -> Tuple[bool, int, int]:
MY_API bool SliderBoolInt2(const char* label, int * value1, int * value2)
{
    *value1 += 1;
    *value2 += 2;
    return false;
}

// -->    def slider_void_int_default_null(label: str, value: Optional[int] = None) -> Tuple[bool, Optional[int]]:
MY_API bool SliderVoidIntDefaultNull(const char* label, int * value = nullptr)
{
    if (value != nullptr)
        *value += 1;
    return true;
}

// -->    def slider_void_int_array(label: str, value: List[int]) -> Tuple[bool, List[int]]:
MY_API bool SliderVoidIntArray(const char* label, int value[3])
{
    value[0] += 1;
    value[1] += 2;
    value[2] += 3;
    return true;
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       mylib/overload_test.h included by mylib/mylib.h                                        //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//
// Test overload
//
MY_API int add_overload(int a, int b) { return a + b; } // type: ignore
MY_API int add_overload(int a, int b, int c) { return a + b + c; } // type: ignore

struct FooOverload // MY_API
{
    MY_API int add_overload(int a, int b) { return a + b; } // type: ignore
    MY_API int add_overload(int a, int b, int c) { return a + b + c; } // type: ignore
};

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       mylib/enum_test.h included by mylib/mylib.h                                            //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// A super nice enum for demo purposes
enum BasicEnum     // MY_API
{
    MyEnum_a = 1, // This is value a
    MyEnum_aa,    // this is value aa
    MyEnum_aaa,   // this is value aaa

    // Lonely comment

    // This is value b
    MyEnum_b,

    // This is c
    // with doc on several lines
    MyEnum_c = MyEnum_a | MyEnum_b,

    // MyEnum_count
};


enum class ClassEnum
{
    On,
    Off,
    Unknown
};



//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//                       mylib/mylib.h continued                                                                //
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
namespace LiterateGeneratorExample // MY_API
{

    // Adds two numbers
    MY_API inline int add(int a, int b) { return a + b; }

    MY_API int sub(int a, int b) { return a - b; }

    MY_API int mul(int a, int b) { return a * b; }

    // A superb struct
    struct Foo            // MY_API
    {
        Foo() { printf("Construct Foo\n");}
        ~Foo() { printf("Destruct Foo\n"); }

        //
        // These are our parameters
        //

        //
        // Test with numeric arrays which should be converted to py::array
        //
        int values[2] = {0, 1};
        bool flags[3] = {false, true, false};

        // These should not be exported (cannot fit in a py::array)
        Point2 points[2];

        // Multiplication factor
        int factor = 10;

        // addition factor
        int delta;

        //
        // And these are our calculations
        //

        // Do some math
        MY_API int calc(int x) { return x * factor + delta; }

        static Foo& Instance() { static Foo instance; return instance; }  // return_value_policy::reference
    };

    MY_API Foo* FooInstance() { return & Foo::Instance(); } // return_value_policy::reference





} // namespace LiterateGeneratorExample