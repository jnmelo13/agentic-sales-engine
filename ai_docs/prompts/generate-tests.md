# Python pytest Unit Test Generator

- Generate comprehensive unit tests using pytest for the specified Python code
- Follow all standards defined in @.cursor/rules/testing.mdc

## Framework Requirements

**Testing Framework:** pytest
**Pattern:** Given-When-Then
**Language:** Python 3.x
**Mocking:** pytest-mock or unittest.mock
**Organization:** Functions only (no classes)
**Documentation:** NO docstrings

## Directory Structure Rule

Tests must mirror the application structure:
- Source: `app/domain/use_case.py`
- Test: `tests/unit/domain/test_use_case.py`

Always maintain this parallel structure.

## Healthcheck

After generating the test file, run pytest to verify that everything is working as expected.

## Test File Structure

```python
import pytest
from app.path.to.module import ClassOrFunction

@pytest.fixture
def fixture_name():
    yield SomeClass()

# 1. Use descriptive naming: test_should_[behavior]_when_[condition]
def test_should_return_result_when_input_valid(fixture_name, mocker):
    # Given
    mock_db = mocker.patch("app.path.db_call", return_value=True)
    
    # When
    result = fixture_name.method("input")
    
    # Then
    assert result == "expected"
    mock_db.assert_called_once()

# 2. Prefer parametrization for multiple scenarios
@pytest.mark.parametrize("input_val, expected", [
    ("a", 1),
    ("b", 2)
])
def test_should_handle_various_inputs(fixture_name, input_val, expected):
    # When
    assert fixture_name.method(input_val) == expected