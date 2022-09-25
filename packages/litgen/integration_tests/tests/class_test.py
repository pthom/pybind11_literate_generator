import lg_mylib


def test_class_doc():
    assert "This is the class doc" in lg_mylib.MyClass.__doc__


def test_class_construction():
    my_struct = lg_mylib.MyClass(factor=42, message="World")
    assert my_struct.factor == 42
    assert my_struct.message == "World"


def test_simple_class_members():
    my_struct = lg_mylib.MyClass()

    my_struct.factor = 42
    assert my_struct.factor == 42


def test_stl_container_members():
    my_struct = lg_mylib.MyClass()
    assert len(my_struct.numbers) == 0

    my_struct.numbers.append(1)
    assert len(my_struct.numbers) == 0

    my_struct.append_number_from_cpp(42)
    assert my_struct.numbers == [42]


def test_fixed_size_numeric_array_members():
    foo = lg_mylib.MyClass()

    assert (foo.values == [0, 1]).all()
    foo.values[0] = 42
    assert (foo.values == [42, 1]).all()

    assert (foo.flags == [False, True, False]).all()
    foo.flags[0] = True
    assert (foo.flags == [True, True, False]).all()

    assert not hasattr(foo, "points")


def test_class_simple_methods():
    my_struct = lg_mylib.MyClass()
    my_struct.set_message("aaa")
    assert my_struct.message == "aaa"


def test_class_static_methods():
    assert lg_mylib.MyClass.static_message() == "Hi!"


def test_struct_not_registered():
    assert "StructNotRegistered" not in dir(lg_mylib)