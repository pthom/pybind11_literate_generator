import os, sys; _THIS_DIR = os.path.dirname(__file__); sys.path = [_THIS_DIR + "/.."] + sys.path
import logging

import srcmlcpp
from srcmlcpp.srcml_types import *
from srcmlcpp import srcml_main
from srcmlcpp import srcml_warnings

from litgen import CodeStyleOptions
from litgen.internal import cpp_to_python, code_utils, code_replacements
from litgen.internal.cpp_function_adapted_params import CppFunctionDeclWithAdaptedParams
from litgen.internal.function_params_adapter import make_function_params_adapter
from litgen.internal.function_wrapper_lambda import \
    make_function_wrapper_lambda_impl, \
    is_default_sizeof_param, is_buffer_size_name_at_idx, is_param_variadic_format


def _add_new_lines(code: str, nb_lines_before: int = 0, nb_lines_after: int = 1) -> str:
    r = "\n" * nb_lines_before + code + "\n" * nb_lines_after
    return r


def _add_one_line_before(code: str) -> str:
    return _add_new_lines(code, nb_lines_before=1)


def _add_two_lines_before(code: str) -> str:
    return _add_new_lines(code, nb_lines_before=2, nb_lines_after=0)


def _add_stub_element(
        cpp_element: CppElementAndComment,
        first_code_line: str,
        options: CodeStyleOptions,
        body_lines: List[str] = [],
        fn_params_and_return: str = ""
    ) -> str:
    """Common layout for class, enum, and functions stubs"""

    location = cpp_to_python.info_original_location_python(cpp_element, options)
    first_line = first_code_line + location

    all_lines_except_first = []
    if len(fn_params_and_return) > 0:
        all_lines_except_first += fn_params_and_return.split("\n")
    all_lines_except_first += cpp_to_python.docstring_lines(cpp_element, options)
    all_lines_except_first += body_lines
    if len(body_lines) == 0:
        all_lines_except_first += ["pass"]

    _i_ = options.indent_python_spaces()
    all_lines_except_first = list(map(lambda s: _i_ + s, all_lines_except_first))

    all_lines_except_first = code_utils.align_python_comments_in_block(all_lines_except_first)

    all_lines = [first_line] + all_lines_except_first

    r = "\n".join(all_lines) + "\n"

    return r


def _make_decl_lines(cpp_decl: CppDecl, options: CodeStyleOptions) -> List[str]:
    var_name = cpp_to_python.decl_python_var_name(cpp_decl, options)
    var_value = cpp_to_python.decl_python_value(cpp_decl, options)
    comment_lines = cpp_to_python.python_comment_lines(cpp_decl, options)

    r = []

    flag_comment_first = cpp_to_python.python_comment_place_on_previous_lines(cpp_decl, options)

    if flag_comment_first:
        r += comment_lines

    decl_line = f"{var_name} = {var_value}"
    if not flag_comment_first:
        decl_line += " " + comment_lines[0]

    r.append(decl_line)

    return r


def _make_enum_element_decl_lines(
        enum: CppEnum,
        enum_element_orig: CppDecl,
        previous_enum_element: CppDecl,
        options: CodeStyleOptions) -> List[str]:

    enum_element = copy.deepcopy(enum_element_orig)

    if cpp_to_python.enum_element_is_count(enum, enum_element, options):
        return []

    if len(enum_element.init) == 0:
        if previous_enum_element is None:
            # the first element of an enum has a default value of 0
            enum_element.init = "0"
            enum_element_orig.init = enum_element.init
        else:
            try:
                previous_value = int(previous_enum_element.init)
                enum_element.init = str(previous_value + 1)
                enum_element_orig.init = enum_element.init
            except ValueError:
                srcml_warnings.emit_srcml_warning(enum_element.srcml_element, """
                        Cannot compute the value of an enum element (previous element value is not an int), it was skipped!
                        """, options.srcml_options)
                return []

    enum_element.name = cpp_to_python.enum_value_name_to_python(enum, enum_element, options)

    #
    # Sometimes, enum decls have interdependent values like this:
    #     enum MyEnum {
    #         MyEnum_a = 1, MyEnum_b,
    #         MyEnum_foo = MyEnum_a | MyEnum_b    //
    #     };
    #
    # So, we search and replace enum strings in the default value (.init)
    #
    for enum_decl in enum.get_enum_decls():
        enum_decl_cpp_name = enum_decl.name_without_array()
        enum_decl_python_name = cpp_to_python.enum_value_name_to_python(enum, enum_decl, options)

        replacement = code_replacements.StringReplacement()
        replacement.replace_what = r"\b" + enum_decl_cpp_name + r"\b"
        replacement.by_what = enum_decl_python_name
        enum_element.init = code_replacements.apply_one_replacement(enum_element.init, replacement)
        #enum_element.init = enum_element.init.replace(enum_decl_cpp_name, enum_decl_python_name)
        #code_utils.w

    return _make_decl_lines(enum_element, options)


#################################
#           Enums
################################

def _generate_pyi_enum(enum: CppEnum, options: CodeStyleOptions) -> str:
    return ""
    first_code_line = f"class {enum.name}(Enum):"

    body_lines: List[str] = []

    previous_enum_element: CppDecl = None
    for child in enum.block.block_children:
        if isinstance(child, CppDecl):
            body_lines += _make_enum_element_decl_lines(enum, child, previous_enum_element, options)
            previous_enum_element = child
        if isinstance(child, CppEmptyLine):
            body_lines.append("")
        if isinstance(child, CppComment):
            body_lines += cpp_to_python.python_comment_lines(child, options)
    r = _add_stub_element(enum, first_code_line, options, body_lines)
    return r


#################################
#           Functions
################################

def _generate_pyi_function(
        function_infos: CppFunctionDecl,
        options: CodeStyleOptions,
        parent_struct_name: str = ""
) -> str:

    function_adapted_params = make_function_params_adapter(function_infos, options, parent_struct_name)

    r = _generate_pyi_function_impl(function_adapted_params, options, parent_struct_name)
    return r


def _paramlist_call_strs(param_list: CppParameterList, options: CodeStyleOptions) -> List[str]:
    r = []
    for param in param_list.parameters:
        param_name_python = cpp_to_python.var_name_to_python(param.decl.name_without_array(), options)
        param_type_cpp = param.decl.cpp_type.str_code()
        param_type_python = cpp_to_python.type_to_python(param_type_cpp, options)
        param_default_value = cpp_to_python.default_value_to_python(param.default_value(), options)

        param_code = f"{param_name_python}: {param_type_python}"
        if len(param_default_value) > 0:
            param_code += f" = {param_default_value}"

        r.append(param_code)
    return r


def _generate_pyi_function_impl(
        function_adapted_params: CppFunctionDeclWithAdaptedParams,
        options: CodeStyleOptions,
        parent_struct_name: str = ""
    ) -> str:

    function_infos = function_adapted_params.function_infos

    function_name_python = cpp_to_python.function_name_to_python(function_infos.name, options)

    return_type_python = cpp_to_python.type_to_python(
        function_infos.full_return_type(options.srcml_options), options)

    first_code_line = f"def {function_name_python}("

    params_strs = _paramlist_call_strs(function_infos.parameter_list, options)
    return_line = f") -> {return_type_python}:"

    # Try to add all params and return type on the same line
    def all_on_one_line():
        first_code_line_full = first_code_line
        first_code_line_full += ", ".join(params_strs)
        first_code_line_full += return_line
        if len(first_code_line_full) < options.python_max_line_length:
            return first_code_line_full
        else:
            return None

    if all_on_one_line() is not None:
        first_code_line = all_on_one_line()
        params_and_return_str = ""
    else:
        params_and_return_str = ",\n".join(params_strs) + "\n" + return_line

    body_lines: List[str] = []

    r = _add_stub_element(function_infos, first_code_line, options, body_lines, params_and_return_str)

    return r

    #
    # Extract from enum:
    #
    # first_code_line = f"class {enum.name}(Enum):"
    #
    # body_lines: List[str] = []
    #
    # previous_enum_element: CppDecl = None
    # for child in enum.block.block_children:
    #     if isinstance(child, CppDecl):
    #         body_lines += _make_enum_element_decl_lines(enum, child, previous_enum_element, options)
    #         previous_enum_element = child
    #     if isinstance(child, CppEmptyLine):
    #         body_lines.append("")
    #     if isinstance(child, CppComment):
    #         body_lines += cpp_to_python.python_comment_lines(child, options)
    # r = _add_stub_element(enum, first_code_line, options, body_lines)
    # return r



    # old pydef code:
    _i_ = options.indent_python_spaces()

    function_infos = function_adapted_params.function_infos
    return_value_policy = _function_return_value_policy(function_infos)

    is_method = len(parent_struct_name) > 0

    fn_name_python = cpp_to_python.function_name_to_python(function_infos.name, options)
    location = info_cpp_element_original_location(function_infos, options)

    module_str = "" if is_method else "m"

    code_lines: List[str] = []
    code_lines += [f'{module_str}.def("{fn_name_python}",{location}']
    lambda_code = make_function_wrapper_lambda_impl(function_adapted_params, options, parent_struct_name)
    lambda_code = code_utils.indent_code(lambda_code, indent_str=_i_)
    code_lines += lambda_code.split("\n")

    pyarg_str = code_utils.indent_code(pyarg_code(function_infos, options),indent_str=options.indent_python_spaces())
    if len(pyarg_str) > 0:
        code_lines += pyarg_str.split("\n")

    #  comment
    comment_cpp =  cpp_to_python.docstring_python_one_line(function_infos.cpp_element_comments.full_comment(), options)
    if len(comment_cpp) == 0:
        # remove last "," from last line since there is no comment that follows
        if code_lines[-1].endswith(","):
            code_lines[-1] = code_lines[-1][ : -1]
    else:
        code_lines += [f'{_i_}"{comment_cpp}"']

    # Return value policy
    if len(return_value_policy) > 0:
        code_lines[-1] += ","
        code_lines += [f"{_i_}pybind11::return_value_policy::{return_value_policy}"]

    # Ending
    if is_method:
        code_lines += ")"
    else:
        code_lines += [');']

    code = "\n".join(code_lines)
    code = code + "\n"
    return code


#################################
#           Methods
################################


def _generate_pyi_constructor(
        function_infos: CppFunctionDecl,
        options: CodeStyleOptions) -> str:
    return ""

    if "delete" in function_infos.specifiers:
        return ""

    """
    A constructor decl look like this
        .def(py::init<ARG_TYPES_LIST>(),
        PY_ARG_LIST
        DOC_STRING);    
    """

    _i_ = options.indent_python_spaces()

    params_str = function_infos.parameter_list.types_only_for_template()
    doc_string = cpp_to_python.docstring_python_one_line(function_infos.cpp_element_comments.full_comment(), options)
    location = info_cpp_element_original_location(function_infos, options)

    code_lines = []
    code_lines.append(f".def(py::init<{params_str}>(){location}")
    code_lines += pyarg_code_list(function_infos, options)
    if len(doc_string) > 0:
        code_lines.append(f'"{doc_string}"')

    # indent lines after first
    for i in range(1, len(code_lines)):
        code_lines[i] = _i_ + code_lines[i]

    code_lines[-1] = code_utils.add_item_before_comment(code_lines[-1], ")")

    code = code_utils.join_lines_with_token_before_comment(code_lines, ",")
    code += "\n"

    return code


def _generate_pyi_method(
        function_infos: CppFunctionDecl,
        options: CodeStyleOptions,
        parent_struct_name: str) -> str:

    return ""

    if function_infos.name == parent_struct_name:
        # Sometimes, srcml might see a constructor as a decl
        # Example:
        # struct Foo
        # {
        #     IMGUI_API Foo();
        # };
        return _generate_pyi_constructor(function_infos, options)
    else:
        return _generate_pyi_function(function_infos, options, parent_struct_name)


#################################
#           Structs and classes
################################


def _add_struct_member_decl(cpp_decl: CppDecl, struct_name: str, options: CodeStyleOptions) -> str:

    return ""

    _i_ = options.indent_python_spaces()
    name_cpp = cpp_decl.name_without_array()
    name_python = cpp_to_python.var_name_to_python(name_cpp, options)
    comment = cpp_decl.cpp_element_comments.full_comment()
    location = info_cpp_element_original_location(cpp_decl, options)

    if len(cpp_decl.range) > 0:
        # We ignore bitfields
        return ""

    if cpp_decl.is_c_array_fixed_size():
        # Cf. https://stackoverflow.com/questions/58718884/binding-an-array-using-pybind11
        array_typename = cpp_decl.cpp_type.str_code()
        if array_typename not in options.c_array_numeric_member_types:
            srcml_warnings.emit_srcml_warning(
                cpp_decl.srcml_element,
                """
                Only numeric C Style arrays are supported 
                    Hint: use a vector, or extend `options.c_array_numeric_member_types`
                """,
                options.srcml_options)
            return ""

        if not options.c_array_numeric_member_flag_replace:
            srcml_warnings.emit_srcml_warning(
                cpp_decl.srcml_element,
                """
                Detected a numeric C Style array, but will not export it.
                    Hint: set `options.c_array_numeric_member_flag_replace = True`
                """,
                options.srcml_options)
            return ""

        array_size = cpp_decl.c_array_size()

        if array_size is None:
            array_size_str = cpp_decl.c_array_size_str()
            if array_size_str in options.c_array_numeric_member_size_dict.keys():
                array_size = options.c_array_numeric_member_size_dict[array_size_str]
                if type(array_size) != int:
                    srcml_warnings.emit_srcml_warning(
                        cpp_decl.srcml_element,
                        """
                        options.c_array_numeric_member_size_dict should contains [str,int] items !
                        """,
                        options.srcml_options)
                    return ""
            else:
                srcml_warnings.emit_srcml_warning(
                    cpp_decl.srcml_element,
                    f"""
                    Detected a numeric C Style array, but will not export it because its size is not parsable.
                        Hint: may be, add the value "{array_size_str}" to `options.c_array_numeric_member_size_dict`
                    """,
                    options.srcml_options)
                return ""

        template_code = f"""
            .def_property("{name_python}", 
                []({struct_name} &self) -> pybind11::array 
                {{
                    auto dtype = pybind11::dtype(pybind11::format_descriptor<{array_typename}>::format());
                    auto base = pybind11::array(dtype, {{{array_size}}}, {{sizeof({array_typename})}});
                    return pybind11::array(dtype, {{{array_size}}}, {{sizeof({array_typename})}}, self.{name_cpp}, base);
                }}, []({struct_name}& self) {{}})
        """

        r = code_utils.unindent_code(template_code, flag_strip_empty_lines=True) + "\n"
        return r

    else:
        code_inner_member  = f'.def_readwrite("MEMBER_NAME_PYTHON", &{struct_name}::MEMBER_NAME_CPP, "MEMBER_COMMENT"){location}\n'
        r = code_inner_member
        r = r.replace("MEMBER_NAME_PYTHON",  name_python)
        r = r.replace("MEMBER_NAME_CPP", name_cpp)
        r = r.replace("MEMBER_COMMENT", cpp_to_python.docstring_python_one_line(comment, options))
        return r


def _add_struct_member_decl_stmt(cpp_decl_stmt: CppDeclStatement, struct_name: str, options: CodeStyleOptions):
    return ""

    r = ""
    for cpp_decl in cpp_decl_stmt.cpp_decls:
        r += _add_struct_member_decl(cpp_decl, struct_name, options)
    return r


def _add_public_struct_elements(public_zone: CppPublicProtectedPrivate, struct_name: str, options: CodeStyleOptions):
    return ""

    r = ""
    for public_child in public_zone.block_children:
        if isinstance(public_child, CppDeclStatement):
            code = _add_struct_member_decl_stmt(cpp_decl_stmt=public_child, struct_name=struct_name, options=options)
            r += code
        # elif isinstance(public_child, CppEmptyLine):
        #     r += "\n"
        # elif isinstance(public_child, CppComment):
        #     r += code_utils.format_cpp_comment_multiline(public_child.cpp_element_comments.full_comment(), 4) + "\n"
        elif isinstance(public_child, CppFunctionDecl):
            code = _generate_pyi_method(function_infos = public_child, options=options, parent_struct_name=struct_name)
            r = r + code
        elif isinstance(public_child, CppConstructorDecl):
            code = _generate_pyi_constructor(function_infos = public_child, options=options)
            r = r + code
    return r


def _generate_pyi_struct_or_class(struct_infos: CppStruct, options: CodeStyleOptions) -> str:
    return ""

    struct_name = struct_infos.name

    if struct_infos.template is not None:
        return ""

    _i_ = options.indent_python_spaces()

    comment = cpp_to_python.docstring_python_one_line(struct_infos.cpp_element_comments.full_comment(), options)
    location = info_cpp_element_original_location(struct_infos, options)

    code_intro = ""
    code_intro += f'auto pyClass{struct_name} = py::class_<{struct_name}>{location}\n'
    code_intro += f'{_i_}(m, "{struct_name}", "{comment}")\n'

    # code_intro += f'{_i_}.def(py::init<>()) \n'  # Yes, we require struct and classes to be default constructible!

    if options.generate_to_string:
        code_outro = f'{_i_}.def("__repr__", [](const {struct_name}& v) {{ return ToString(v); }});'
    else:
        code_outro = f'{_i_};'

    r = code_intro

    if not struct_infos.has_non_default_ctor() and not struct_infos.has_deleted_default_ctor():
        r += f"{_i_}.def(py::init<>()) // implicit default constructor\n"
    if struct_infos.has_deleted_default_ctor():
        r += f"{_i_}// (default constructor explicitly deleted)\n"

    for child in struct_infos.block.block_children:
        if child.tag() == "public":
            zone_code = _add_public_struct_elements(public_zone=child, struct_name=struct_name, options=options)
            r += code_utils.indent_code(zone_code, indent_str=options.indent_python_spaces())
    r = r + code_outro
    r = r + "\n"
    return r


#################################
#           Namespace
################################
def _generate_pyi_namespace(
        cpp_namespace: CppNamespace,
        options: CodeStyleOptions,
        current_namespaces: List[str] = []) -> str:

    namespace_name = cpp_namespace.name
    new_namespaces = current_namespaces + [namespace_name]
    namespace_code = generate_pyi(cpp_namespace.block, options, new_namespaces)
    location = cpp_to_python.info_original_location_python(cpp_namespace, options)

    namespace_code_commented = ""
    namespace_code_commented += f"# <namespace {namespace_name}>{location}\n"
    namespace_code_commented += namespace_code
    namespace_code_commented += f"# </namespace {namespace_name}>"

    namespace_code_commented += "\n"
    return namespace_code_commented


#################################
#           All
################################

def generate_pyi(
        cpp_unit: CppUnit,
        options: CodeStyleOptions,
        current_namespaces: List[str] = [],
        add_boxed_types_definitions: bool = False) -> str:

    r = ""
    for i, cpp_element in enumerate(cpp_unit.block_children):
        if False:
            pass
        elif isinstance(cpp_element, CppFunctionDecl) or isinstance(cpp_element, CppFunction):
            r += _add_one_line_before( _generate_pyi_function(cpp_element, options, parent_struct_name="") )
        elif isinstance(cpp_element, CppEnum):
            r += _add_two_lines_before( _generate_pyi_enum(cpp_element, options) )
        elif isinstance(cpp_element, CppStruct) or isinstance(cpp_element, CppClass):
            r += _add_two_lines_before( _generate_pyi_struct_or_class(cpp_element, options) )
        elif isinstance(cpp_element, CppNamespace):
            r += _add_two_lines_before( _generate_pyi_namespace(cpp_element, options, current_namespaces) )

    if add_boxed_types_definitions:
        pass
        # boxed_structs = cpp_to_python.BoxedImmutablePythonType.struct_codes()
        # boxed_bindings = cpp_to_python.BoxedImmutablePythonType.binding_codes(options)
        # if len(boxed_structs) > 0:
        #     r = boxed_structs + "\n" + boxed_bindings + "\n" + r

    r = code_utils.code_set_max_consecutive_empty_lines(r, options.python_max_consecutive_empty_lines)
    return r