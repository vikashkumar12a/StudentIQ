
import io
import pandas as pd
import pytest

from app import analyze_data, app, REQUIRED_COLUMNS


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def valid_data():
    """Create a valid sample student dataset."""

    return pd.DataFrame(
        [
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
        ]
    )






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


def test_average_attendance_calculation():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    assert b"85.8" in response.data


def test_highest_and_lowest_subject():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    assert b"Highest Scoring Subject" in response.data
    assert b"Lowest Scoring Subject" in response.data


def test_subject_averages_are_calculated_correctly():
    df = pd.DataFrame({
        "Roll_No": ["201", "202"],
        "Name": ["Aman", "Ravi"],
        "Gender": ["Male", "Male"],
        "Python": [80, 100],
        "Maths": [40, 60],
        "English": [50, 70],
        "Science": [60, 80],
        "Attendance": [90, 95],
    })

    result = analyze_data(df)

    assert result["Python"].mean() == 90
    assert result["Maths"].mean() == 50
    assert result["English"].mean() == 60
    assert result["Science"].mean() == 70
    assert len(REQUIRED_COLUMNS) == 8


def test_marks_with_decimal_values(valid_data):
    """Decimal marks should be accepted and percentage calculated correctly."""

    valid_data["Python"] = valid_data["Python"].astype(float)
    valid_data.loc[0, "Python"] = 85.5

    result = analyze_data(valid_data)

    rahul = result[result["Roll_No"] == "101"].iloc[0]

    assert rahul["Python"] == 85.5
    assert rahul["Total"] == 335.5
    assert rahul["Percentage"] == 83.88


def test_non_numeric_marks_are_rejected(valid_data):
    """Marks containing text should be rejected."""

    valid_data["Python"] = valid_data["Python"].astype(object)
    valid_data.loc[0, "Python"] = "abc"

    with pytest.raises(ValueError):
        analyze_data(valid_data)


def test_missing_marks_are_rejected(valid_data):
    """Missing subject marks should be rejected."""

    valid_data.loc[0, "Python"] = float("nan")

    with pytest.raises(ValueError):
        analyze_data(valid_data)


def test_duplicate_student_records(valid_data):
    """Completely duplicated student records should be rejected."""

    duplicate_row = valid_data.iloc[[0]]
    duplicate_data = pd.concat(
        [valid_data, duplicate_row],
        ignore_index=True,
    )

    with pytest.raises(
        ValueError,
        match="Duplicate roll numbers are not allowed",
    ):
        analyze_data(duplicate_data)

def test_empty_student_name_rejected(valid_data):
    valid_data.loc[0, "Name"] = "   "


    with pytest.raises(ValueError, match="name"):
        analyze_data(valid_data)


def test_empty_roll_number_rejected(valid_data):
    valid_data.loc[0, "Roll_No"] = "   "


    with pytest.raises(ValueError, match="roll number"):
        analyze_data(valid_data)


def test_empty_gender_rejected(valid_data):
    valid_data.loc[0, "Gender"] = "   "


    with pytest.raises(ValueError, match="Gender cannot be empty"):
        analyze_data(valid_data)

def test_infinite_marks_rejected(valid_data):
    valid_data["Python"] = valid_data["Python"].astype(float)
    valid_data.loc[0, "Python"] = float("inf")


    with pytest.raises(ValueError, match="finite numbers"):
        analyze_data(valid_data)


def test_decimal_marks_allowed(valid_data):
    valid_data["Python"] = valid_data["Python"].astype(float)
    valid_data.loc[0, "Python"] = 85.5


    result = analyze_data(valid_data)

    assert result.loc[0, "Python"] == 85.5


def test_upload_no_file_selected(client):
    response = client.post(
        "/",
        data={},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert b"Please select a CSV file." in response.data


def test_upload_wrong_file_extension(client):
    data = {
        "dataset": (
            io.BytesIO(b"test data"),
            "students.txt",
        )
    }

    response = client.post(
        "/",
        data=data,
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert b"Please upload a CSV file." in response.data



def test_get_data_file_not_found(monkeypatch, tmp_path):
    import app as app_module

    missing_file = tmp_path / "missing_students.csv"

    monkeypatch.setattr(
        app_module,
        "DATA_FILE",
        missing_file,
    )

    with pytest.raises(
        FileNotFoundError,
        match="Student dataset not found",
    ):
        app_module.get_data()


def test_get_data_empty_csv(monkeypatch, tmp_path):
    import app as app_module

    empty_file = tmp_path / "students.csv"
    empty_file.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        app_module,
        "DATA_FILE",
        empty_file,
    )

    with pytest.raises(
        ValueError,
        match="saved students.csv file is empty",
    ):
        app_module.get_data()





def test_get_data_invalid_csv(monkeypatch, tmp_path):
    import app as app_module

    invalid_file = tmp_path / "students.csv"

    invalid_file.write_text(
        "Roll_No,Name,Gender,Python,Maths,English,Science,Attendance\n"
        '101,"Rahul,Male,80,75,90,85,95\n'
        "102,Priya,Female,90,88,92,95,98,EXTRA",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        app_module,
        "DATA_FILE",
        invalid_file,
    )

    with pytest.raises(
        ValueError,
        match="invalid CSV format",
    ):
        app_module.get_data()





def test_analyze_data_duplicate_student_records():
    import pandas as pd
    import pytest

    from app import analyze_data

    data = {
        "Roll_No": ["101", "101"],
        "Name": ["Rahul", "Rahul"],
        "Gender": ["Male", "Male"],
        "Python": [80, 80],
        "Maths": [75, 75],
        "English": [90, 90],
        "Science": [85, 85],
        "Attendance": [95, 95],
    }

    df = pd.DataFrame(data)

    with pytest.raises(
        ValueError,
        match="Duplicate roll numbers",
    ):
        analyze_data(df)




def test_get_data_invalid_encoding(monkeypatch, tmp_path):
    import app as app_module

    invalid_file = tmp_path / "students.csv"

    invalid_file.write_bytes(b"\xff\xfe\xfa\xfb")

    monkeypatch.setattr(
        app_module,
        "DATA_FILE",
        invalid_file,
    )

    with pytest.raises(
        ValueError,
        match="invalid text encoding",
    ):
        app_module.get_data()



def test_upload_valid_csv(client, monkeypatch, tmp_path):
    import io
    import app as app_module

    data_file = tmp_path / "data" / "students.csv"

    monkeypatch.setattr(
        app_module,
        "DATA_FILE",
        data_file,
    )

    csv_content = (
        "Roll_No,Name,Gender,Python,Maths,English,Science,Attendance\n"
        "101,Rahul,Male,80,75,90,85,95\n"
    )

    response = client.post(
        "/",
        data={
            "dataset": (
                io.BytesIO(csv_content.encode("utf-8")),
                "students.csv",
            )
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert data_file.exists()

    saved_df = app_module.pd.read_csv(data_file)

    assert len(saved_df) == 1
    assert saved_df.loc[0, "Name"] == "Rahul"


def test_search_student_by_name(client):
    response = client.get("/?search=Rahul")

    assert response.status_code == 200
    assert b"Rahul" in response.data





def test_upload_empty_csv(client):
    import io

    response = client.post(
        "/",
        data={
            "dataset": (
                io.BytesIO(b""),
                "students.csv",
            )
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert b"CSV file is empty" in response.data





def test_download_report(client):
    response = client.get("/download")

    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert (
        "student_performance_report.csv"
        in response.headers["Content-Disposition"]
    )








def test_upload_unexpected_error(client, monkeypatch):
    import io
    import app as app_module

    original_read_csv = app_module.pd.read_csv

    def raise_unexpected_error(*args, **kwargs):
        if hasattr(args[0], "filename"):
            raise RuntimeError("Unexpected test error")

        return original_read_csv(*args, **kwargs)

    monkeypatch.setattr(
        app_module.pd,
        "read_csv",
        raise_unexpected_error,
    )

    response = client.post(
        "/",
        data={
            "dataset": (
                io.BytesIO(
                    b"Roll_No,Name,Gender,Python,Maths,English,Science,Attendance\n"
                    b"101,Rahul,Male,80,75,90,85,95\n"
                ),
                "students.csv",
            )
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert (
        b"Upload failed due to an unexpected error."
        in response.data
    )




def test_download_report_error(client, monkeypatch):
    import app as app_module

    def raise_load_error():
        raise ValueError("Test report error")

    monkeypatch.setattr(
        app_module,
        "get_data",
        raise_load_error,
    )

    response = client.get("/download")

    assert response.status_code == 500
    assert response.data == b"Unable to generate the report."


def test_get_data_read_csv_file_not_found(monkeypatch, tmp_path):
    import app as app_module

    data_file = tmp_path / "students.csv"
    data_file.write_text(
        "temporary file",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        app_module,
        "DATA_FILE",
        data_file,
    )

    def raise_file_not_found(*args, **kwargs):
        raise FileNotFoundError("File disappeared")

    monkeypatch.setattr(
        app_module.pd,
        "read_csv",
        raise_file_not_found,
    )

    with pytest.raises(
        ValueError,
        match="The students.csv file was not found.",
    ):
        app_module.get_data()




def test_dashboard_dataset_error(client, monkeypatch):
    import app as app_module

    def raise_load_error():
        raise ValueError("Test dataset error")

    monkeypatch.setattr(
        app_module,
        "get_data",
        raise_load_error,
    )

    response = client.get("/")

    assert response.status_code == 500
    assert (
        b"Dataset error. Check data/students.csv "
        b"and the terminal output for details."
        in response.data
    )




def test_negative_marks_are_rejected(valid_data):
    """Negative marks should be rejected."""

    valid_data.loc[0, "Python"] = -5

    with pytest.raises(
        ValueError,
        match="Marks cannot be negative",
    ):
        analyze_data(valid_data)


def test_marks_above_100_are_rejected(valid_data):
    """Marks above 100 should be rejected."""

    valid_data.loc[0, "Python"] = 101

    with pytest.raises(
        ValueError,
        match="Marks cannot exceed 100",
    ):
        analyze_data(valid_data)



def test_negative_attendance_is_rejected(valid_data):
    """Negative attendance should be rejected."""

    valid_data.loc[0, "Attendance"] = -1

    with pytest.raises(
        ValueError,
        match="Attendance must be between 0 and 100",
    ):
        analyze_data(valid_data)


def test_attendance_above_100_is_rejected(valid_data):
    """Attendance above 100 should be rejected."""

    valid_data.loc[0, "Attendance"] = 101

    with pytest.raises(
        ValueError,
        match="Attendance must be between 0 and 100",
    ):
        analyze_data(valid_data)




def test_invalid_gender_upload_preserves_existing_data(
    tmp_path,
    monkeypatch,
):
    import app as student_app

    app.config["TESTING"] = True

    original_data = pd.DataFrame(
        {
            "Roll_No": ["101"],
            "Name": ["Rahul"],
            "Gender": ["Male"],
            "Python": [80],
            "Maths": [75],
            "English": [85],
            "Science": [90],
            "Attendance": [95],
        }
    )

    data_file = tmp_path / "students.csv"
    original_data.to_csv(data_file, index=False)

    monkeypatch.setattr(
        student_app,
        "DATA_FILE",
        data_file,
    )

    invalid_data = original_data.copy()
    invalid_data.loc[0, "Roll_No"] = "102"
    invalid_data.loc[0, "Name"] = "Aman"
    invalid_data.loc[0, "Gender"] = "InvalidGender"

    csv_content = invalid_data.to_csv(index=False).encode("utf-8")

    with app.test_client() as client:
        response = client.post(
            "/",
            data={
                "dataset": (
                    io.BytesIO(csv_content),
                    "invalid_gender.csv",
                )
            },
            content_type="multipart/form-data",
        )

    assert response.status_code == 200

    saved_data = pd.read_csv(data_file)

    assert str(saved_data["Roll_No"].iloc[0]) == "101"
    assert saved_data["Name"].iloc[0] == "Rahul"
    assert saved_data["Gender"].iloc[0] == "Male"
