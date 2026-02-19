import pytest
from unittest.mock import MagicMock

# Assuming the main.py is located at examples/complex_app/main.py
# We need to import the function directly for testing.
# For mocking, we will patch the modules where they are imported within main.py.
# The full path to the module containing process_data is examples.complex_app.main.
from examples.complex_app.main import process_data


def test_process_data_happy_path(mocker):
    """
    Tests the process_data function with valid input, ensuring all dependencies
    are called correctly and the final output is as expected.
    """
    # Mock the external dependencies
    mock_add = mocker.patch('examples.complex_app.main.add', return_value=30)
    mock_get_user = mocker.patch('examples.complex_app.main.get_user', return_value={'id': 1, 'name': 'John Doe'})
    mock_to_upper = mocker.patch('examples.complex_app.main.to_upper', return_value="USER JOHN DOE HAS VALUE 30")

    # Call the function under test
    result = process_data("some_data")

    # Assertions
    assert result == "USER JOHN DOE HAS VALUE 30"
    mock_add.assert_called_once_with(10, 20)
    mock_get_user.assert_called_once_with(1)
    mock_to_upper.assert_called_once_with("User John Doe has value 30")


def test_process_data_with_none_input(mocker):
    """
    Tests process_data with None as input, expecting it to return None
    without calling any external dependencies.
    """
    # Mock dependencies to ensure they are not called
    mock_add = mocker.patch('examples.complex_app.main.add')
    mock_get_user = mocker.patch('examples.complex_app.main.get_user')
    mock_to_upper = mocker.patch('examples.complex_app.main.to_upper')

    # Call the function under test
    result = process_data(None)

    # Assertions
    assert result is None
    mock_add.assert_not_called()
    mock_get_user.assert_not_called()
    mock_to_upper.assert_not_called()


def test_process_data_with_empty_string_input(mocker):
    """
    Tests process_data with an empty string as input, expecting it to return None
    without calling any external dependencies.
    """
    # Mock dependencies to ensure they are not called
    mock_add = mocker.patch('examples.complex_app.main.add')
    mock_get_user = mocker.patch('examples.complex_app.main.get_user')
    mock_to_upper = mocker.patch('examples.complex_app.main.to_upper')

    # Call the function under test
    result = process_data("")

    # Assertions
    assert result is None
    mock_add.assert_not_called()
    mock_get_user.assert_not_called()
    mock_to_upper.assert_not_called()


def test_process_data_add_returns_different_value(mocker):
    """
    Tests process_data when the 'add' dependency returns a different value,
    ensuring the final output reflects this change.
    """
    # Mock dependencies with a different return for 'add'
    mock_add = mocker.patch('examples.complex_app.main.add', return_value=50)
    mock_get_user = mocker.patch('examples.complex_app.main.get_user', return_value={'id': 1, 'name': 'John Doe'})
    mock_to_upper = mocker.patch('examples.complex_app.main.to_upper', return_value="USER JOHN DOE HAS VALUE 50")

    # Call the function under test
    result = process_data("some_data")

    # Assertions
    assert result == "USER JOHN DOE HAS VALUE 50"
    mock_add.assert_called_once_with(10, 20)
    mock_get_user.assert_called_once_with(1)
    mock_to_upper.assert_called_once_with("User John Doe has value 50")


def test_process_data_get_user_returns_different_user(mocker):
    """
    Tests process_data when the 'get_user' dependency returns a different user,
    ensuring the final output reflects this change.
    """
    # Mock dependencies with a different return for 'get_user'
    mock_add = mocker.patch('examples.complex_app.main.add', return_value=30)
    mock_get_user = mocker.patch('examples.complex_app.main.get_user', return_value={'id': 2, 'name': 'Jane Smith'})
    mock_to_upper = mocker.patch('examples.complex_app.main.to_upper', return_value="USER JANE SMITH HAS VALUE 30")

    # Call the function under test
    result = process_data("some_data")

    # Assertions
    assert result == "USER JANE SMITH HAS VALUE 30"
    mock_add.assert_called_once_with(10, 20)
    mock_get_user.assert_called_once_with(1)
    mock_to_upper.assert_called_once_with("User Jane Smith has value 30")


def test_process_data_to_upper_receives_correct_string(mocker):
    """
    Tests that the 'to_upper' dependency is called with the correctly formatted
    intermediate string before it's converted to uppercase.
    """
    # Mock dependencies
    mock_add = mocker.patch('examples.complex_app.main.add', return_value=30)
    mock_get_user = mocker.patch('examples.complex_app.main.get_user', return_value={'id': 1, 'name': 'Alice'})
    mock_to_upper = mocker.patch('examples.complex_app.main.to_upper', return_value="USER ALICE HAS VALUE 30")

    # Call the function under test
    process_data("some_data")

    # Assert that to_upper was called with the exact expected string
    expected_intermediate_string = "User Alice has value 30"
    mock_to_upper.assert_called_once_with(expected_intermediate_string)


def test_process_data_get_user_missing_name_key(mocker):
    """
    Tests process_data's behavior when 'get_user' returns a dictionary
    missing the 'name' key, expecting a KeyError during string formatting.
    """
    mock_add = mocker.patch('examples.complex_app.main.add', return_value=30)
    # Simulate get_user returning a dict without 'name'
    mock_get_user = mocker.patch('examples.complex_app.main.get_user', return_value={'id': 1})
    mock_to_upper = mocker.patch('examples.complex_app.main.to_upper')

    with pytest.raises(KeyError) as excinfo:
        process_data("some_data")

    assert "'name'" in str(excinfo.value)
    mock_add.assert_called_once_with(10, 20)
    mock_get_user.assert_called_once_with(1)
    mock_to_upper.assert_not_called()


def test_process_data_add_raises_exception(mocker):
    """
    Tests process_data's behavior when the 'add' dependency raises an exception.
    """
    mock_add = mocker.patch('examples.complex_app.main.add', side_effect=ValueError("Addition failed"))
    mock_get_user = mocker.patch('examples.complex_app.main.get_user')
    mock_to_upper = mocker.patch('examples.complex_app.main.to_upper')

    with pytest.raises(ValueError, match="Addition failed"):
        process_data("some_data")

    mock_add.assert_called_once_with(10, 20)
    mock_get_user.assert_not_called()
    mock_to_upper.assert_not_called()


def test_process_data_get_user_raises_exception(mocker):
    """
    Tests process_data's behavior when the 'get_user' dependency raises an exception.
    """
    mock_add = mocker.patch('examples.complex_app.main.add', return_value=30)
    mock_get_user = mocker.patch('examples.complex_app.main.get_user', side_effect=ConnectionError("API down"))
    mock_to_upper = mocker.patch('examples.complex_app.main.to_upper')

    with pytest.raises(ConnectionError, match="API down"):
        process_data("some_data")

    mock_add.assert_called_once_with(10, 20)
    mock_get_user.assert_called_once_with(1)
    mock_to_upper.assert_not_called()


def test_process_data_to_upper_raises_exception(mocker):
    """
    Tests process_data's behavior when the 'to_upper' dependency raises an exception.
    """
    mock_add = mocker.patch('examples.complex_app.main.add', return_value=30)
    mock_get_user = mocker.patch('examples.complex_app.main.get_user', return_value={'id': 1, 'name': 'John Doe'})
    mock_to_upper = mocker.patch('examples.complex_app.main.to_upper', side_effect=TypeError("Invalid string"))

    with pytest.raises(TypeError, match="Invalid string"):
        process_data("some_data")

    mock_add.assert_called_once_with(10, 20)
    mock_get_user.assert_called_once_with(1)
    mock_to_upper.assert_called_once_with("User John Doe has value 30")