import pytest
import importlib.util
import sys
import os

@pytest.fixture(scope="module")
def empty_module_path(tmp_path_factory):
    """
    Creates a temporary empty Python file for testing.
    This ensures the test is runnable and isolated, not relying on a specific
    pre-existing file path from the prompt.
    """
    temp_dir = tmp_path_factory.mktemp("empty_module_test")
    empty_file = temp_dir / "empty_file_to_test.py"
    empty_file.write_text("")  # Ensure it's empty
    return empty_file

@pytest.fixture
def imported_empty_module(empty_module_path):
    """
    Imports the temporary empty module dynamically and yields the module object.
    Ensures proper cleanup from sys.modules after the test.
    """
    module_name = "empty_file_to_test"
    spec = importlib.util.spec_from_file_location(module_name, str(empty_module_path))
    if spec is None:
        pytest.fail(f"Could not find module spec for {empty_module_path}")

    module = importlib.util.module_from_spec(spec)
    # Add to sys.modules to simulate a real import and allow exec_module to work correctly
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as e:
        pytest.fail(f"Importing an empty file raised an unexpected error: {e}")

    yield module

    # Cleanup: remove the module from sys.modules to prevent interference with other tests
    if module_name in sys.modules:
        del sys.modules[module_name]

def test_empty_file_imports_without_error(imported_empty_module):
    """
    Tests that an empty Python file can be imported without raising any errors.
    The `imported_empty_module` fixture handles the import process, and if
    any error occurs during import, it will cause the test to fail.
    This test simply asserts that a module object was successfully obtained.
    """
    assert imported_empty_module is not None, "Module object should be successfully imported."

def test_empty_file_defines_no_user_content(imported_empty_module):
    """
    Tests that an empty Python file, when imported, does not define any
    user-created functions, classes, or variables.
    It should only contain standard module attributes (dunders).
    """
    module = imported_empty_module

    # Get all attributes from the module's dictionary.
    # This is more precise than dir() as it shows what was *defined* in the module.
    module_dict_keys = set(module.__dict__.keys())

    # Filter out attributes that start with '__'. These are typically standard
    # module attributes added by the Python interpreter.
    # Any remaining non-dunder attributes would indicate user-defined content.
    non_dunder_attributes = {attr for attr in module_dict_keys if not attr.startswith('__')}

    assert not non_dunder_attributes, \
        f"Empty file defined unexpected non-dunder attributes: {non_dunder_attributes}"

def test_empty_file_has_none_docstring(imported_empty_module):
    """
    Tests that an empty Python file, when imported, has a `__doc__` attribute
    that is `None`, as no docstring is provided in an empty file.
    """
    assert imported_empty_module.__doc__ is None, "Docstring of an empty file should be None."

def test_empty_file_has_correct_name(imported_empty_module):
    """
    Tests that the imported empty module has the correct `__name__` attribute,
    which should match the name used for import.
    """
    assert imported_empty_module.__name__ == "empty_file_to_test", \
        f"Expected module name 'empty_file_to_test', got {imported_empty_module.__name__}"

def test_empty_file_has_correct_file_path(imported_empty_module, empty_module_path):
    """
    Tests that the imported empty module has the correct `__file__` attribute,
    pointing to the path of the temporary empty file.
    Paths are normalized for robust comparison across different operating systems.
    """
    expected_path = os.path.normcase(os.path.abspath(str(empty_module_path)))
    actual_path = os.path.normcase(os.path.abspath(imported_empty_module.__file__))
    assert actual_path == expected_path, \
        f"Expected __file__ '{expected_path}', got '{actual_path}'"

def test_empty_file_is_not_a_package(imported_empty_module):
    """
    Tests that an empty Python file is not considered a package.
    For a simple, top-level .py file imported directly, `__package__` should be
    an empty string, and `__path__` should not be present.
    """
    module = imported_empty_module
    assert module.__package__ == "", \
        f"Expected __package__ to be empty string, got '{module.__package__}'"
    assert not hasattr(module, '__path__'), \
        "An empty .py file should not have a __path__ attribute (it's not a package)."