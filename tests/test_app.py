
import io
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

def test_missing_required_column(valid_data):
    invalid_data = valid_data.drop(columns=["Maths"])

    with pytest.raises(ValueError, match="Missing columns"):
        analyze_data(invalid_data)

def test_duplicate_column_names(valid_data):
    duplicate_data = valid_data.copy()

    duplicate_data.columns = [
        "Roll_No",
        "Name",
        "Gender",
        "Python",
        "Maths",
        "English",
        "Attendance",
        "Attendance",
    ]

    with pytest.raises(
        ValueError,
        match="Duplicate column names are not allowed",
    ):
        analyze_data(duplicate_data)
   
def test_empty_csv_upload():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.post(
            "/",
            data={
                "dataset": (
                    io.BytesIO(b""),
                    "empty.csv",
                )
            },
            content_type="multipart/form-data",
        )

    assert response.status_code == 200
    assert b"CSV file is empty" in response.data


def test_invalid_csv_format():
    app.config["TESTING"] = True

    invalid_csv = b'Roll_No,Name\n101,"Rahul'

    with app.test_client() as client:
        response = client.post(
            "/",
            data={
                "dataset": (
                    io.BytesIO(invalid_csv),
                    "invalid.csv",
                )
            },
            content_type="multipart/form-data",
        )

    assert response.status_code == 200
    assert b"Invalid CSV format" in response.data

def test_file_size_limit():
    app.config["TESTING"] = True

    large_csv = b"A" * (6 * 1024 * 1024)

    with app.test_client() as client:
        response = client.post(
            "/",
            data={
                "dataset": (
                    io.BytesIO(large_csv),
                    "large.csv",
                )
            },
            content_type="multipart/form-data",
        )

    assert response.status_code == 413


def test_invalid_csv_encoding():
    app.config["TESTING"] = True

    invalid_csv = b"\xff\xfe\xfa\xfb"

    with app.test_client() as client:
        response = client.post(
            "/",
            data={
                "dataset": (
                    io.BytesIO(invalid_csv),
                    "invalid_encoding.csv",
                )
            },
            content_type="multipart/form-data",
        )

    assert response.status_code == 200
    assert b"error" in response.data.lower()

def test_invalid_upload_preserves_existing_data(tmp_path, monkeypatch):
    import app as student_app

    app.config["TESTING"] = True

    original_data = pd.DataFrame({
        "Roll_No": ["101"],
        "Name": ["Rahul"],
        "Gender": ["Male"],
        "Python": [80],
        "Maths": [75],
        "English": [85],
        "Science": [90],
        "Attendance": [95],
    })

    data_file = tmp_path / "students.csv"
    original_data.to_csv(data_file, index=False)

    monkeypatch.setattr(student_app, "DATA_FILE", data_file)

    invalid_data = pd.DataFrame({
        "Roll_No": ["102"],
        "Name": ["Aman"],
        "Gender": ["Male"],
        "Python": [150],
        "Maths": [75],
        "English": [85],
        "Science": [90],
        "Attendance": [95],
    })

    csv_content = invalid_data.to_csv(index=False).encode("utf-8")

    with app.test_client() as client:
        response = client.post(
            "/",
            data={
                "dataset": (
                    io.BytesIO(csv_content),
                    "invalid.csv",
                )
            },
            content_type="multipart/form-data",
        )

    assert response.status_code == 200

    saved_data = pd.read_csv(data_file)

    assert str(saved_data["Roll_No"].iloc[0]) == "101"
    assert saved_data["Name"].iloc[0] == "Rahul"