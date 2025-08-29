import numpy as np
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from footballmodels.clustering.features import four_factor_model  # Import your function
from sklearn.preprocessing import MinMaxScaler


# Create a mock DataFrame for testing
def create_mock_dataframe():
    data = pd.DataFrame(
        {
            "x": [3, 2, 3],
            "y": [4, 5, 6],
            "endX": [7, 8, 9],
            "endY": [10, 11, 12],
            "qualifiers": [
                [{"type": {"value": 1, "displayName": "Angle"}, "value": 45}],
                [{"type": {"value": 1, "displayName": "Angle"}, "value": 30}],
                [{"type": {"value": 1, "displayName": "Angle"}, "value": 60}],
            ],
        }
    )
    return data


@patch("footballmodels.clustering.features.col_get_qualifier_value", return_value=np.array([45, 30, 60]))
@patch("footballmodels.clustering.features.progressive_distance", return_value=np.array([2, 6, 4]))
@patch(
    "footballmodels.clustering.features.load_model",
    return_value=MagicMock(
        transform=MagicMock(return_value=np.array([[1.0, 0.0, 0.5, 0.0], [0.0, 0.5, 0.0, 1.0], [1.0, 1.0, 1.0, 0.5]]))
    ),
)
def test_four_factor_model(preprocessor_mock, mock_progressive_distance, mock_col_get_qualifier_value):
    # Create a mock DataFrame
    data = create_mock_dataframe()

    # Call the function
    result = four_factor_model(data)

    # Check that the external functions were called with the correct arguments
    mock_col_get_qualifier_value.assert_called_once_with(data, display_name="Angle")
    mock_progressive_distance.assert_called_once_with(data)

    # Check that MinMaxScaler's transform method was called with the correct arguments
    preprocessor_mock.assert_called_once_with("pass_scaler")
    transform_call_arg = preprocessor_mock.return_value.transform.call_args_list[0][0][0]
    np.testing.assert_array_almost_equal(transform_call_arg, np.array([[3, 4, 2, 45], [2, 5, 6, 30], [3, 6, 4, 60]]))
    # Check the result
    expected_result = np.array([[1.0, 0.0, 0.5, 0.0], [0.0, 0.5, 0.0, 1.0], [1.0, 1.0, 1.0, 0.5]])
    np.testing.assert_array_almost_equal(result, expected_result)


if __name__ == "__main__":
    pytest.main()
