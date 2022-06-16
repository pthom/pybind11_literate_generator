from __future__ import annotations
import copy
from typing import List, Optional
import logging
from dataclasses import dataclass

import xml.etree.ElementTree as ET  # noqa

from codemanip import code_utils, CodePosition
from srcmlcpp import srcml_utils, srcml_caller
from srcmlcpp.srcml_options import SrcmlOptions


@dataclass
class CppElementComments:
    """Gathers the C++ comments about functions, declarations, etc. : each CppElement can store
     comment on previous lines, and a single line comment next to its declaration.

    Lonely comments are stored as `CppComment`

     Example:
         `````cpp
         /*
         A multiline C comment
         about Foo1
         */
         void Foo1();

         // First line of comment on Foo2()
         // Second line of comment on Foo2()
         void Foo2();

         // A lonely comment

         //
         // Another lonely comment, on two lines
         // which ends on this second line, but has surrounding empty lines
         //

         // A comment on top of Foo3() & Foo4(), which should be kept as a standalone comment
         // since Foo3 and Foo4 have eol comments
         Void Foo3(); // Comment on end of line for Foo3()
         Void Foo4(); // Comment on end of line for Foo4()
         // A comment that shall not be grouped to the previous (which was an EOL comment for Foo4())
         ````
    """

    comment_on_previous_lines: str
    comment_end_of_line: str

    def __init__(self):
        self.comment_on_previous_lines = ""
        self.comment_end_of_line = ""

    def comment(self):
        if len(self.comment_on_previous_lines) > 0 and len(self.comment_end_of_line) > 0:
            return self.comment_on_previous_lines + "\n" + self.comment_end_of_line
        else:
            return self.comment_on_previous_lines + self.comment_end_of_line

    def as_dict(self):
        r = {
            "comment_top": self.comment_on_previous_lines,
            "comment_eol": self.comment_end_of_line,
        }
        return r

    def top_comment_code(self):
        top_comments = map(lambda comment: "//" + comment, self.comment_on_previous_lines.splitlines())
        top_comment = "\n".join(top_comments)
        if len(top_comment) > 0:
            top_comment += "\n"
        return top_comment

    def eol_comment_code(self):
        if len(self.comment_end_of_line) == 0:
            return ""
        else:
            return " //" + self.comment_end_of_line

    def add_eol_comment(self, comment):
        if len(self.comment_end_of_line) == 0:
            self.comment_end_of_line = comment
        else:
            self.comment_end_of_line += " - " + comment

    def full_comment(self):
        if len(self.comment_on_previous_lines) > 0 and len(self.comment_end_of_line) > 0:
            return self.comment_on_previous_lines + "\n\n" + self.comment_end_of_line
        else:
            return self.comment_on_previous_lines + self.comment_end_of_line


class CppElement:
    """Wrapper around a srcLML xml node."""

    srcml_element: ET.Element

    def __init__(self, srcml_element: ET.Element):
        assert isinstance(srcml_element, ET.Element)
        self.srcml_element = srcml_element

    def tag(self) -> str:
        assert self.srcml_element.tag is not None
        return srcml_utils.clean_tag_or_attrib(self.srcml_element.tag)

    def text_or_empty(self) -> str:
        """Text part of the xml element.
        Warning: Will return empty string if not found"""
        return srcml_utils.str_or_empty(self.srcml_element.text)

    def tail_or_empty(self):
        """Tail part of the xml element"""
        return srcml_utils.str_or_empty(self.srcml_element.tail)

    def start(self) -> Optional[CodePosition]:
        """Start position in the C++ code"""
        return srcml_utils.element_start_position(self.srcml_element)

    def end(self) -> Optional[CodePosition]:
        """End position in the C++ code"""
        return srcml_utils.element_end_position(self.srcml_element)

    def has_name(self) -> bool:
        name_children = srcml_utils.children_with_tag(self.srcml_element, "name")
        return len(name_children) == 1

    def name_code(self) -> Optional[str]:
        """Returns the C++ code corresponding to the name extracted from the srcML xml tree.

        * In simple cases, it will be a simple text extraction, for example with the code:
            int a = 10;
          The decl name node will look like
            <name>a</name>

        * Sometimes, we will need to call srcml to reconstruct the code.
          For example, with the code:
            int* a[10];
          The decl name node will look like
               <name>
                    <name>a</name>
                    <index>[
                        <expr>
                            <literal type="number">10</literal>
                        </expr>]
                    </index>
                </name>
        """
        if not self.has_name():
            return None
        name_element = srcml_utils.child_with_tag(self.srcml_element, "name")
        assert name_element is not None
        if name_element.text is not None:
            return name_element.text
        else:
            return srcml_caller.srcml_to_code(name_element)

    def attribute_value(self, attr_name):
        if attr_name in self.srcml_element.attrib:
            return self.srcml_element.attrib[attr_name]
        else:
            return None

    def str_code_verbatim(self) -> str:
        """Return the exact C++ code from which this xml node was constructed by calling the executable srcml"""
        return srcml_caller.srcml_to_code(self.srcml_element)

    def annotate_with_cpp_element_class(self, msg):
        class_name = str(self.__class__)
        items = class_name.split(".")
        class_name = items[-1][:-2]
        return f"[++{class_name}++]  {msg} [--{class_name}--]"

    def str_code(self):
        """Returns a C++ textual representation of the contained code element.
        By default, it returns an exact copy of the original code. Derived classes override this implementation
        with their own information and the generated code might differ a little from the original code.
        """
        return self.str_code_verbatim()

    def str_xml_readable(self):
        """Return the xml tree formatted in a yaml inspired format"""
        return srcml_utils.srcml_to_str_readable(self.srcml_element)

    def str_xml(self):
        """Returns the xml tree as a xml string representation"""
        return srcml_utils.srcml_to_str(self.srcml_element)

    def as_dict(self):
        as_dict = {
            "tag": self.tag(),
            "name": code_utils.str_or_none_token(self.name_code()),
            "text": self.text_or_empty(),
            "start": str(self.start()),
            "end": str(self.end()),
        }
        return as_dict

    def __str__(self):
        return self.str_xml_readable()


@dataclass
class CppElementAndComment(CppElement):
    """A CppElement to which we add comments"""

    cpp_element_comments: CppElementComments

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        assert isinstance(element, ET.Element)
        super().__init__(element)
        self.cpp_element_comments = cpp_element_comments

    def as_dict(self):
        as_dict = code_utils.merge_dicts(super().as_dict(), self.cpp_element_comments.as_dict())
        return as_dict

    def str_commented(self, is_enum: bool = False, is_decl_stmt: bool = False):
        result = self.cpp_element_comments.top_comment_code()
        result += self.str_code()
        if is_enum:
            result += ","
        if is_decl_stmt:
            result += ";"
        result += self.cpp_element_comments.eol_comment_code()
        return result

    def __str__(self):
        return self.str_commented()


@dataclass
class CppEmptyLine(CppElementAndComment):
    def __init__(self, element: ET.Element):
        dummy_comments = CppElementComments()
        super().__init__(element, dummy_comments)

    def str_code(self):
        return ""

    def str_commented(self, is_enum: bool = False, is_decl_stmt: bool = False):  # noqa
        return ""

    def __str__(self):
        return ""


class CppUnprocessed(CppElementAndComment):
    """Any Cpp Element that is not yet processed by srcmlcpp
    We keep its original source under the form of a string
    """

    code: str

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)
        self.code = ""

    def str_code(self):
        return f"<unprocessed_{self.tag()}/>"

    def __str__(self):
        return self.str_commented()


@dataclass
class CppBlock(CppElementAndComment):
    """The class CppBlock is a container that represents any set of code  detected by srcML.
    It has several derived classes.

     - For namespaces:
             Inside srcML we have this: <block>CODE</block>
             Inside python, the block is handled by `CppBlock`
     - For files (i.e "units"):
             Inside srcML we have this: <unit>CODE</unit>
             Inside python, the block is handled by `CppUnit` (which derives from `CppBlock`)
     - For functions and anonymous block:
             Inside srcML we have this:  <block><block_content>CODE</block_content></block>
             Inside python, the block is handled by `CppBlockContent` (which derives from `CppBlock`)
     - For classes and structs:
             Inside srcML we have this: <block><private or public>CODE</private or public></block>
             Inside python, the block is handled by `CppPublicProtectedPrivate` (which derives from `CppBlock`)

     https://www.srcml.org/doc/cpp_srcML.html#block
    """

    block_children: List[CppElementAndComment]

    def __init__(self, element: ET.Element):
        dummy_cpp_comments = CppElementComments()
        super().__init__(element, dummy_cpp_comments)
        self.block_children: List[CppElementAndComment] = []

    def str_block(self, is_enum: bool = False):
        result = ""
        for i, child in enumerate(self.block_children):
            if i < len(self.block_children) - 1:
                child_str = child.str_commented(is_enum=is_enum)
            else:
                child_str = child.str_commented(is_enum=False)
            result += child_str
            if not child_str.endswith("\n"):
                result += "\n"
        return result

    def __str__(self):
        return self.str_block()


@dataclass
class CppUnit(CppBlock):
    """A kind of block representing a full file."""

    def __init__(self, element: ET.Element):
        super().__init__(element)

    def __str__(self):
        return self.str_block()


@dataclass
class CppBlockContent(CppBlock):
    """A kind of block used by function and anonymous blocks, where the code is inside <block><block_content>
    This can be viewed as a sub-block with a different name
    """

    def __init__(self, element: ET.Element):
        super().__init__(element)

    def __str__(self):
        return self.str_block()


@dataclass
class CppPublicProtectedPrivate(CppBlock):  # Also a CppElementAndComment
    """A kind of block defined by a public/protected/private zone in a struct or in a class

    See https://www.srcml.org/doc/cpp_srcML.html#public-access-specifier
    Note: this is not a direct adaptation. Here we merge the different access types, and we derive from CppBlockContent
    """

    access_type: str = ""  # "public", "private", or "protected"
    default_or_explicit: str = ""  # "default" or "" ("default" means it was added automatically)

    def __init__(self, element: ET.Element, access_type: str, default_or_explicit: str):
        super().__init__(element)
        assert default_or_explicit in [None, "", "default"]
        assert access_type in ["public", "protected", "private"]
        self.access_type = access_type
        self.default_or_explicit = default_or_explicit

    def str_ppp(self):
        r = ""

        r += f"{self.access_type}" + ":"
        if self.default_or_explicit == "default":
            r += "// <default_access_type/>"
        r += "\n"

        r += code_utils.indent_code(self.str_block(), 4)
        return r

    def str_code(self):
        return self.str_ppp()

    def str_commented(self, is_enum: bool = False, is_decl_stmt: bool = False):  # noqa
        return self.str_code()

    def __str__(self):
        return self.str_ppp()


@dataclass
class CppType(CppElement):
    """
    Describes a full C++ type, as seen by srcML
    See https://www.srcml.org/doc/cpp_srcML.html#type

    A type name can be composed of several names, for example:

        "unsigned int" -> ["unsigned", "int"]

        MY_API void Process() declares a function whose return type will be ["MY_API", "void"]
                             (where "MY_API" could for example be a dll export/import macro)

    Note about composed types:
        For composed types, like `std::map<int, std::string>` srcML returns a full tree.
        In order to simplify the process, we recompose this kind of type names into a simple string
    """

    typenames: List[str]

    # specifiers: could be ["const"], ["static", "const"], ["extern"], ["constexpr"], etc.
    specifiers: List[str]

    # modifiers: could be ["*"], ["&&"], ["&"], ["*", "*"], ["..."]
    modifiers: List[str]

    # template arguments types i.e ["int"] for vector<int>
    # (this will not be filled: see note about composed types)
    # argument_list: List[str]

    def __init__(self, element: ET.Element):
        super().__init__(element)
        self.typenames: List[str] = []
        self.specifiers: List[str] = []
        self.modifiers: List[str] = []

    @staticmethod
    def authorized_modifiers():
        return ["*", "&", "&&", "..."]

    def str_code(self):
        nb_const = self.specifiers.count("const")

        if nb_const > 2:
            raise ValueError("I cannot handle more than two `const` occurrences in a type!")

        specifiers = self.specifiers
        if nb_const == 2:
            # remove the last const and handle it later
            specifier_r: List[str] = list(reversed(specifiers))
            specifier_r.remove("const")
            specifiers = list(reversed(specifier_r))

        specifiers_str = code_utils.join_remove_empty(" ", specifiers)
        modifiers_str = code_utils.join_remove_empty(" ", self.modifiers)

        name = " ".join(self.typenames)

        name_and_arg = name
        strs = [specifiers_str, name_and_arg, modifiers_str]
        r = code_utils.join_remove_empty(" ", strs)

        if nb_const == 2:
            r += " const"

        return r

    def is_const(self):
        return "const" in self.specifiers

    def __str__(self):
        return self.str_code()


@dataclass
class CppDecl(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration
    """

    cpp_type: CppType

    # decl_name, i.e. the variable name
    decl_name: str = ""

    # c_array_code will only be filled if this decl looks like:
    #   *  `int a[]:`      <-- in this case, c_array_code="[]"
    #   or
    #   *  `int a[10]:`      <-- in this case, c_array_code="[10]"
    #
    # In other cases, it will be an empty string
    c_array_code: str = ""

    # * init represent the initial aka default value.
    # With srcML, it is inside an <init><expr> node in srcML.
    # Here we retransform it to C++ code for simplicity
    #
    #     For example:
    #     int a = 5;
    #
    #     leads to:
    #     <decl_stmt><decl><type><name>int</name></type> <name>a</name> <init>= <expr><literal type="number">5</literal></expr></init></decl>;</decl_stmt>
    #
    #     Which is transcribed as "5"
    initial_value_code: str = ""  # initial or default value

    bitfield_range: str = ""  # Will be filled for bitfield members

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def str_code(self):
        r = ""
        if hasattr(self, "cpp_type"):
            r += str(self.cpp_type) + " "
        r += self.decl_name + self.c_array_code
        if len(self.initial_value_code) > 0:
            r += " = " + self.initial_value_code
        return r

    def type_name_default_for_signature(self):
        r = ""
        if hasattr(self, "cpp_type"):
            r += str(self.cpp_type) + " "
        r += self.decl_name + self.c_array_code
        if len(self.initial_value_code) > 0:
            r += " = " + self.initial_value_code
        return r

    def has_name_or_ellipsis(self):
        assert self.decl_name is not None
        if len(self.decl_name) > 0:
            return True
        elif "..." in self.cpp_type.modifiers:
            return True
        return False

    def __str__(self):
        r = self.str_commented()
        return r

    def is_c_string_list_ptr(self):
        """
        Returns true if this decl looks like a const C string double pointer.
        Examples:
            const char * const items[]
            const char ** const items
            const char ** items
        :return:
        """
        is_const = "const" in self.cpp_type.specifiers
        is_char = self.cpp_type.typenames == ["char"]
        is_default_init = (
            self.initial_value_code == "" or self.initial_value_code == "NULL" or self.initial_value_code == "nullptr"
        )

        nb_indirections = 0
        nb_indirections += self.cpp_type.modifiers.count("*")
        if len(self.c_array_code) > 0:
            nb_indirections += 1

        r = is_const and is_char and nb_indirections == 2 and is_default_init
        return r

    def is_c_array(self) -> bool:
        """
        Returns true if this decl is a C style array, e.g.
            int v[4]
        or
            int v[]
        """
        return len(self.c_array_code) > 0

    def c_array_size(self) -> Optional[int]:
        """
        If this decl is a c array, return its size, e.g. for
            int v[4]
        It will return 4
        """
        if not self.is_c_array():
            return None
        pos = self.c_array_code.index("[")
        size_str = self.c_array_code[pos + 1: -1]
        try:
            size = int(size_str)
            return size
        except ValueError:
            return None

    def is_c_array_fixed_size(self):
        """Returns true if this decl is a c array, and has a fixed size"""
        return self.c_array_size() is not None

    def is_const(self):
        """
        Returns true if this decl is const"""
        return "const" in self.cpp_type.specifiers  # or "const" in self.cpp_type.names

    def c_array_fixed_size_to_std_array(self) -> CppDecl:
        """
        Processes decl that contains a *const* c style array of fixed size, e.g. `const int v[2]`

        We simply wrap it into a std::array, like this:
                `const int v[2]` --> `const std::array<int, 2> v`
        """
        is_const = "const" in self.cpp_type.specifiers

        assert self.is_c_array_fixed_size()
        assert is_const

        # If the array is `const`, then we simply wrap it into a std::array, like this:
        # `const int v[2]` --> `[ const std::array<int, 2> v ]`
        new_decl = copy.deepcopy(self)
        new_decl.c_array_code = ""

        new_decl.cpp_type.specifiers.remove("const")
        cpp_type_name = new_decl.cpp_type.str_code()

        std_array_type_name = f"std::array<{cpp_type_name}, {self.c_array_size()}>&"
        new_decl.cpp_type.typenames = [std_array_type_name]

        new_decl.cpp_type.specifiers.append("const")
        new_decl.decl_name = new_decl.decl_name
        return new_decl

    def is_immutable_for_python(self) -> bool:
        from litgen.internal import cpp_to_python

        cpp_type_name = self.cpp_type.str_code()
        r = cpp_to_python.is_cpp_type_immutable_for_python(cpp_type_name)
        return r

    def c_array_fixed_size_to_new_boxed_decls(self) -> List[CppDecl]:
        """
        Processes decl that contains a *non const* c style array of fixed size, e.g. `int v[2]`
            * we may need to "Box" the values if they are of an immutable type in python,
            * we separate the array into several arguments
            For example:
                `int v[2]`
            Becomes:
                `[ BoxedInt v_0, BoxedInt v_1 ]`

        :return: a list of CppDecls as described before
        """
        from litgen.internal import cpp_to_python

        is_const = "const" in self.cpp_type.specifiers

        assert self.is_c_array_fixed_size()
        assert not is_const

        cpp_type_name = self.cpp_type.str_code()

        if cpp_to_python.is_cpp_type_immutable_for_python(cpp_type_name):
            boxed_type = cpp_to_python.BoxedImmutablePythonType(cpp_type_name)
            cpp_type_name = boxed_type.boxed_type_name()

        n = self.c_array_size()
        assert n is not None

        new_decls = []
        for i in range(n):
            new_decl = copy.deepcopy(self)
            new_decl.decl_name = new_decl.decl_name + "_" + str(i)
            new_decl.cpp_type.typenames = [cpp_type_name]
            new_decl.cpp_type.modifiers = ["&"]
            new_decl.c_array_code = ""
            new_decls.append(new_decl)

        return new_decls


@dataclass
class CppDeclStatement(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#variable-declaration-statement
    """

    cpp_decls: List[CppDecl]  # A CppDeclStatement can initialize several variables

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)
        self.cpp_decls: List[CppDecl] = []

    def str_code(self):
        str_decls = list(
            map(
                lambda cpp_decl: cpp_decl.str_commented(is_decl_stmt=True),
                self.cpp_decls,
            )
        )
        str_decl = code_utils.join_remove_empty("\n", str_decls)
        return str_decl

    def __str__(self):
        return self.str_commented()


@dataclass
class CppParameter(CppElement):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """

    decl: CppDecl

    template_type: CppType  # This is only for template's CppParameterList
    template_name: str = ""

    def __init__(self, element: ET.Element):
        super().__init__(element)

    def type_name_default_for_signature(self):
        if not hasattr(self, "decl"):
            breakpoint()
        assert hasattr(self, "decl")
        r = self.decl.type_name_default_for_signature()
        return r

    def str_code(self):
        if hasattr(self, "decl"):
            assert not hasattr(self, "template_type")
            return str(self.decl)
        else:
            if not hasattr(self, "template_type"):
                logging.warning("CppParameter.__str__() with no decl and no template_type")
            return str(self.template_type) + " " + self.template_name

    def str_template_type(self):
        assert hasattr(self, "template_type")
        r = str(self.template_type) + " " + self.template_name
        return r

    def __str__(self):
        return self.str_code()

    def full_type(self) -> str:
        r = self.decl.cpp_type.str_code()
        return r

    def default_value(self):
        return self.decl.initial_value_code

    def variable_name(self):
        return self.decl.decl_name


@dataclass
class CppParameterList(CppElement):
    """
    List of parameters of a function
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """

    parameters: List[CppParameter]

    def __init__(self, element: ET.Element):
        super().__init__(element)
        self.parameters = []

    def types_names_default_for_signature_list(self):
        """Returns a list like ["int a", "bool flag = true"] """
        params_strs = list(map(lambda param: param.type_name_default_for_signature(), self.parameters))
        return params_strs

    def types_names_default_for_signature_str(self):
        """Returns a string like "int a, bool flag = true" """
        params_strs = self.types_names_default_for_signature_list()
        params_str = ", ".join(params_strs)
        return params_str

    def str_code(self):
        return self.types_names_default_for_signature_str()

    def names_only_for_call(self):
        names = [param.variable_name() for param in self.parameters]
        r = ", ".join(names)
        return r

    def types_only_for_template(self):
        types = [param.full_type() for param in self.parameters]
        r = ", ".join(types)
        return r

    def __str__(self):
        return self.str_code()


@dataclass
class CppTemplate(CppElement):
    """
    Template parameters of a function, struct or class
    https://www.srcml.org/doc/cpp_srcML.html#template
    """

    parameter_list: CppParameterList

    def __init__(self, element: ET.Element):
        super().__init__(element)
        self.parameter_list = CppParameterList(element)

    def str_code(self):
        typelist = [param.str_template_type() for param in self.parameter_list.parameters]
        typelist_str = ", ".join(typelist)
        params_str = f"template<{typelist_str}>\n"
        return params_str

    def __str__(self):
        return self.str_code()


@dataclass
class CppFunctionDecl(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-declaration
    """

    specifiers: List[str]  # "const" or ""
    return_type: CppType
    parameter_list: CppParameterList
    template: CppTemplate
    is_auto_decl: bool  # True if it is a decl of the form `auto square(double) -> double`
    function_name: str

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)
        self.specifiers: List[str] = []
        self.is_auto_decl = False
        self.function_name = ""

    def _str_signature(self):
        r = ""

        if hasattr(self, "template"):
            r += f"template<{str(self.template)}>"

        r += f"{self.return_type} {self.function_name}({self.parameter_list})"

        if len(self.specifiers) > 0:
            specifiers_strs = map(str, self.specifiers)
            r = r + " ".join(specifiers_strs)

        return r

    def str_code(self):
        r = self._str_signature() + ";"
        return r

    def full_return_type(self, options: SrcmlOptions):
        r = self.return_type.str_code()
        for prefix in options.functions_api_prefixes:
            r = r.replace(prefix + " ", "")
        if r.startswith("inline "):
            r = r.replace("inline ", "")
        return r

    def is_const(self):
        return "const" in self.specifiers

    def __str__(self):
        return self.str_commented()


@dataclass
class CppFunction(CppFunctionDecl):
    """
    https://www.srcml.org/doc/cpp_srcML.html#function-definition
    """

    block: CppUnprocessed

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def str_code(self):
        r = self._str_signature() + str(self.block)
        return r

    def __str__(self):
        r = ""
        if len(self.cpp_element_comments.top_comment_code()) > 0:
            r += self.cpp_element_comments.top_comment_code()
        r += self._str_signature() + self.cpp_element_comments.eol_comment_code()
        r += "\n" + str(self.block) + "\n"
        return r


@dataclass
class CppConstructorDecl(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#constructor-declaration
    """

    specifiers: List[str]
    parameter_list: CppParameterList
    constructor_name: str  # will be equal to the class or struct name

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)
        self.specifiers: List[str] = []
        self.constructor_name = ""

    def _str_signature(self):
        r = f"{self.constructor_name}({self.parameter_list})"
        if len(self.specifiers) > 0:
            specifiers_strs = map(str, self.specifiers)
            r = r + " " + " ".join(specifiers_strs)
        return r

    def str_code(self):
        return self._str_signature()

    def __str__(self):
        return self.str_commented()


@dataclass
class CppConstructor(CppConstructorDecl):
    """
    https://www.srcml.org/doc/cpp_srcML.html#constructor
    """

    block: CppUnprocessed
    member_init_list: CppUnprocessed

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def str_code(self):
        r = self._str_signature() + str(self.block)
        return r

    def __str__(self):
        r = ""
        if len(self.cpp_element_comments.top_comment_code()) > 0:
            r += self.cpp_element_comments.top_comment_code()
        r += self._str_signature() + self.cpp_element_comments.eol_comment_code()
        r += "\n" + str(self.block) + "\n"
        return r


@dataclass
class CppSuper(CppElement):
    """
    Define a super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """

    specifier: str = ""  # public, private or protected inheritance
    superclass_name: str = ""  # name of the super class

    def __init__(self, element: ET.Element):
        super().__init__(element)

    def str_code(self):
        if len(self.specifier) > 0:
            return f"{self.specifier} {self.superclass_name}"
        else:
            return self.superclass_name

    def __str__(self):
        return self.str_code()


@dataclass
class CppSuperList(CppElement):
    """
    Define a list of super classes of a struct or class
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """

    super_list: List[CppSuper]

    def __init__(self, element: ET.Element):
        super().__init__(element)
        self.super_list: List[CppSuper] = []

    def str_code(self):
        strs = list(map(str, self.super_list))
        return " : " + code_utils.join_remove_empty(", ", strs)

    def __str__(self):
        return self.str_code()


@dataclass
class CppStruct(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#struct-definition
    """

    class_name: str  # either the class or the struct name
    super_list: CppSuperList
    block: CppBlock
    template: CppTemplate  # for template classes or structs

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)
        self.class_name = ""

    def str_code(self):
        r = ""
        if hasattr(self, "template"):
            r += str(self.template)

        if isinstance(self, CppClass):
            r += "class "
        elif isinstance(self, CppStruct):
            r += "struct "
        r += f"{self.class_name}"

        if hasattr(self, "super_list") and len(str(self.super_list)) > 0:
            r += str(self.super_list)

        r += "\n"

        r += "{\n"
        r += code_utils.indent_code(str(self.block), 4)
        r += "};\n"

        return r

    def __str__(self):
        return self.str_commented()

    def has_non_default_ctor(self) -> bool:
        found_non_default_ctor = False
        for access_zone in self.block.block_children:
            if isinstance(access_zone, CppPublicProtectedPrivate):
                for child in access_zone.block_children:
                    if isinstance(child, CppConstructorDecl):
                        found_non_default_ctor = True
                        break
                    if isinstance(child, CppFunctionDecl) and child.function_name == self.class_name:
                        found_non_default_ctor = True
                        break

        return found_non_default_ctor

    def has_deleted_default_ctor(self) -> bool:
        found_deleted_default_ctor = False
        for access_zone in self.block.block_children:
            if isinstance(access_zone, CppPublicProtectedPrivate):
                for child in access_zone.block_children:
                    if isinstance(child, CppConstructorDecl):
                        if "delete" in child.specifiers:
                            found_deleted_default_ctor = True
                            break
        return found_deleted_default_ctor

    def is_templated_class(self):
        return hasattr(self, "template")

@dataclass
class CppClass(CppStruct):
    """
    https://www.srcml.org/doc/cpp_srcML.html#class-definition
    """

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def __str__(self):
        return self.str_commented()


@dataclass
class CppComment(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#comment
    Warning, the text contains "//" or "/* ... */" and "\n"
    """

    comment: str

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def str_code(self):
        lines = self.comment.split("\n")  # split("\n") keeps empty lines (splitlines() does not!)
        lines = list(map(lambda s: "// " + s, lines))
        return "\n".join(lines)

    def __str__(self):
        return self.str_code()


@dataclass
class CppNamespace(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#namespace
    """

    ns_name: str
    block: CppBlock

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)
        self.ns_name = ""

    def str_code(self):
        r = f"namespace {self.ns_name}\n"
        r += "{\n"
        r += code_utils.indent_code(str(self.block), 4)
        r += "}"
        return r

    def __str__(self):
        return self.str_code()


@dataclass
class CppEnum(CppElementAndComment):
    """
    https://www.srcml.org/doc/cpp_srcML.html#enum-definition
    https://www.srcml.org/doc/cpp_srcML.html#enum-class
    """

    block: CppBlock
    enum_type: str = ""  # "class" or ""
    enum_name: str = ""

    def __init__(self, element: ET.Element, cpp_element_comments: CppElementComments):
        super().__init__(element, cpp_element_comments)

    def str_code(self):
        r = ""
        if self.enum_type == "class":
            r += f"enum class {self.enum_name}\n"
        else:
            r += f"enum {self.enum_name}\n"
        r += "{\n"
        block_code = self.block.str_block(is_enum=True)
        r += code_utils.indent_code(block_code, 4)
        r += "};\n"
        return r

    def __str__(self):
        return self.str_code()

    def get_enum_decls(self) -> List[CppDecl]:
        r: List[CppDecl] = []
        for child in self.block.block_children:
            if isinstance(child, CppDecl):
                r.append(child)
        return r
