# import pytest

# # run from terminal:
# #         pytest -q test_sysexit.py

# # pytest --fixtures   # shows builtin and custom fixtures

# # Links:
# #     https://docs.pytest.org/en/latest/getting-started.html
# #     https://docs.pytest.org/en/latest/how-to/mark.html#mark
# #     https://docs.pytest.org/en/latest/how-to/usage.html#usage

# # CLI:
# #     Run tests in a module:
# #         pytest test_mod.py
# #     ---------------------------------
    
# #     Run tests in a directory
# #         pytest testing/
# #     ---------------------------------
# #     Run tests by keyword expressions
# #         pytest -k "MyClass and not method"
# #     ---------------------------------

#     # To run a specific test within a module:
#     #     pytest test_mod.py::test_func
    
#     # Another example specifying a test method in the command line:
#     #     pytest test_mod.py::TestClass::test_method
    
#     # Run tests by marker expressions
#     #     pytest -m slow
    
#     # To get a list of the slowest 10 test durations over 1.0s long:
#     #     pytest --durations=10 --durations-min=1.0
    
# #!! Dont include an __init__.py file in the test directory as breaks relative imports for pytest


# def f():
#     raise SystemExit(1)


# def test_mytest():
#     with pytest.raises(SystemExit):
#         f()
        
# # content of test_class.py
# class TestClass: # ClassName must be prefixed with Test, methods must also start with test.
#     def test_one(self):
#         x = "this"
#         assert "h" in x

#     def test_two(self):
#         x = "hello"
#         assert hasattr(x, "check")