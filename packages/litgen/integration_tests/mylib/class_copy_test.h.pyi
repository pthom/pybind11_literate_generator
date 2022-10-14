# ============================================================================
# This file was autogenerated
# It is presented side to side with its source: class_copy_test.h
#    (see integration_tests/bindings/lg_mylib/__init__pyi which contains the full
#     stub code, including this code)
# ============================================================================

# type: ignore

# <litgen_stub> // Autogenerated code below! Do not edit!
####################    <generated_from:class_copy_test.h>    ####################


class Copyable_ImplicitCopyCtor:
    a: int = 1


class Copyable_ExplicitCopyCtor:
    def __init__(self) -> None:
        pass
    def __init__(self, other: Copyable_ExplicitCopyCtor) -> None:
        pass
    a: int = 1


class Copyable_ExplicitPrivateCopyCtor:
    def __init__(self) -> None:
        pass
    a: int = 1



class Copyable_DeletedCopyCtor:
    a: int = 1
    def __init__(self) -> None:
        pass


# <submodule AAA>
class AAA:  # Proxy class that introduces typings for the *submodule* AAA
    pass  # (This corresponds to a C++ namespace. All method are static!)
    #  ------------------------------------------------------------------------
    #      <template specializations for class Copyable_Template>
    class Copyable_TemplateInt:
        value: int
    #      </template specializations for class Copyable_Template>
    #  ------------------------------------------------------------------------

# </submodule AAA>
####################    </generated_from:class_copy_test.h>    ####################

# </litgen_stub> // Autogenerated code end!
