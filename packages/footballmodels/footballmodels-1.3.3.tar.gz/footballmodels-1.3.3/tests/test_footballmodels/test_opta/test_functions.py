import pandas as pd
import pytest
from footballmodels.opta.functions import in_defensive_box, in_attacking_box


def test_in_defensive_box_start():
    # Create a mock DataFrame
    data = pd.DataFrame(
        {
            "x": [10, 20, 5, 5],
            "y": [25, 30, 40, 90],
            "endX": [15, 25, 10, 7],
            "endY": [35, 40, 50, 90],
        }
    )

    # Call the function
    result = in_defensive_box(data, start=True)

    # Check the result
    expected_result = pd.Series([True, False, True, False])
    pd.testing.assert_series_equal(result, expected_result)


def test_in_defensive_box_end():
    # Create a mock DataFrame
    data = pd.DataFrame(
        {
            "endX": [10, 20, 5, 5],
            "endY": [25, 30, 40, 90],
            "x": [15, 25, 10, 8],
            "y": [35, 40, 50, 90],
        }
    )

    # Call the function
    result = in_defensive_box(data, start=False)

    # Check the result
    expected_result = pd.Series([True, False, True, False])
    pd.testing.assert_series_equal(result, expected_result)


def test_in_attacking_box_start():
    # Create a mock DataFrame
    data = pd.DataFrame(
        {
            "x": [90, 80, 95, 95],
            "y": [25, 30, 40, 10],
            "endX": [15, 25, 10, 90],
            "endY": [35, 40, 50, 10],
        }
    )

    # Call the function
    result = in_attacking_box(data, start=True)

    # Check the result
    expected_result = pd.Series([True, False, True, False])
    pd.testing.assert_series_equal(result, expected_result)


def test_in_attacking_box_end():
    # Create a mock DataFrame
    data = pd.DataFrame(
        {
            "endX": [90, 80, 95, 95],
            "endY": [25, 30, 40, 10],
            "x": [15, 25, 10, 90],
            "y": [35, 40, 50, 10],
        }
    )

    # Call the function
    result = in_attacking_box(data, start=False)

    # Check the result
    expected_result = pd.Series([True, False, True, False])
    pd.testing.assert_series_equal(result, expected_result)


if __name__ == "__main__":
    pytest.main()
