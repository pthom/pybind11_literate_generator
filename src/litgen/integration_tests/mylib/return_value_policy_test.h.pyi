# ============================================================================
# This file was autogenerated
# It is presented side to side with its source: return_value_policy_test.h
#    (see integration_tests/bindings/lg_mylib/__init__pyi which contains the full
#     stub code, including this code)
# ============================================================================

# type: ignore

# <litgen_stub> // Autogenerated code below! Do not edit!
####################    <generated_from:return_value_policy_test.h>    ####################

#
# return_value_policy:
#
# If a function has an end-of-line comment which contains `return_value_policy::reference`,
# and if this function returns a pointer or a reference, litgen will automatically add
# `pybind11::return_value_policy::reference` when publishing it.
#
# Notes: `reference` could be replaced by `take_ownership`, or any other member of `pybind11::return_value_policy`
#
# You can also set a global options for matching functions names that return a reference or a pointer
#     see
#             LitgenOptions.fn_return_force_policy_reference_for_pointers__regex
#     and
#             LitgenOptions.fn_return_force_policy_reference_for_references__regex: str = ""

class MyConfig:
    #
    # For example, singletons (such as the method below) should be returned as a reference,
    # otherwise python might destroy the singleton instance as soon as it goes out of scope.
    #

    @staticmethod
    def instance() -> MyConfig:
        """py::return_value_policy::reference"""
        pass
    value: int = 0
    def __init__(self, value: int = 0) -> None:
        """Auto-generated default constructor with named params"""
        pass

def my_config_instance() -> MyConfig:
    """py::return_value_policy::reference"""
    pass

####################    </generated_from:return_value_policy_test.h>    ####################

# </litgen_stub> // Autogenerated code end!
