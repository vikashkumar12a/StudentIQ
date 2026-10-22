
import pandas as pd
import pytest

from app import analyze_data, app, REQUIRED_COLUMNS


@pytest.fixture
def valid_data():
    """Create a valid sample student dataset."""

    return pd.DataFrame([
        {
            "Roll_No": "101",
            "Name": "Rahul",
            "Gender": "Male",
            "Python": 80,
            "Maths": 75,
            "English": 90,
            "Science": 85,
            "Attendance": 95,
        },
        {
            "Roll_No": "102",
            "Name": "Priya",
            "Gender": "Female",
            "Python": 90,
            "Maths": 88,
            "English": 92,
            "Science": 95,
            "Attendance": 98,
        },
    ])


def test_valid_data(valid_data):
    result = analyze_data(valid_data)

    assert len(result) == 2
    assert "Percentage" in result.columns
    assert "Total" in result.columns
    assert "Result" in result.columns


def test_percentage_calculation(valid_data):
    result = analyze_data(valid_data)

    rahul = result[result["Roll_No"] == "101"].iloc[0]

    assert rahul["Total"] == 330
    assert rahul["Percentage"] == 82.5


def test_empty_dataset():
    empty_df = pd.DataFrame(columns=REQUIRED_COLUMNS)

    with pytest.raises(ValueError, match="empty"):
        analyze_data(empty_df)


def test_marks_above_100(valid_data):
    valid_data.loc[0, "Python"] = 150

    with pytest.raises(ValueError, match="cannot exceed 100"):
        analyze_data(valid_data)


def test_negative_marks(valid_data):
    valid_data.loc[0, "Python"] = -5

    with pytest.raises(ValueError, match="cannot be negative"):
        analyze_data(valid_data)


def test_duplicate_roll_numbers(valid_data):
    valid_data.loc[1, "Roll_No"] = "101"

    with pytest.raises(ValueError, match="Duplicate roll numbers"):
        analyze_data(valid_data)


def test_invalid_gender(valid_data):
    valid_data.loc[0, "Gender"] = "Unknown123"

    with pytest.raises(ValueError, match="Gender must be"):
        analyze_data(valid_data)


def test_invalid_attendance(valid_data):
    valid_data.loc[0, "Attendance"] = 150

    with pytest.raises(ValueError, match="Attendance must be"):
        analyze_data(valid_data)


def test_fail_if_any_subject_below_35(valid_data):
    valid_data.loc[0, "Maths"] = 20

    result = analyze_data(valid_data)

    rahul = result[result["Roll_No"] == "101"].iloc[0]

    assert rahul["Result"] == "Fail"


def test_dashboard_page():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200

