
from flask import Flask, render_template, request, send_file
import pandas as pd
import numpy as np
from pathlib import Path
from io import BytesIO


app = Flask(__name__)

# Maximum uploaded file size: 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "students.csv"


# Subjects and required CSV columns
SUBJECTS = ["Python", "Maths", "English", "Science"]

REQUIRED_COLUMNS = [
    "Roll_No",
    "Name",
    "Gender",
    "Python",
    "Maths",
    "English",
    "Science",
    "Attendance",
]


def analyze_data(df):
    """Validate student data and calculate performance metrics."""

    if df.empty:
        raise ValueError("CSV file is empty. Please upload student data.")

    # Normalize column names by removing surrounding spaces
    df.columns = df.columns.astype(str).str.strip()

    # Check required columns
    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))

    # Keep only required columns
    df = df[REQUIRED_COLUMNS].copy()

    # Normalize names and roll numbers
    df["Roll_No"] = df["Roll_No"].astype("string").str.strip()
    df["Name"] = df["Name"].astype("string").str.strip()

    # Check missing and empty names or roll numbers
    if (
        df["Roll_No"].isna().any()
        or df["Name"].isna().any()
        or df["Roll_No"].eq("").any()
        or df["Name"].eq("").any()
    ):
        raise ValueError("Every student must have a roll number and name.")
 

    # Check duplicate roll numbers
    if df["Roll_No"].duplicated().any():
        raise ValueError("Duplicate roll numbers are not allowed.")

    # Validate gender values
    df["Gender"] = (
        df["Gender"]
        .astype("string")
        .str.strip()
        .str.title()
    )

    allowed_genders = ["Male", "Female", "Other"]

    if df["Gender"].isna().any() or df["Gender"].eq("").any():
        raise ValueError("Gender cannot be empty.")

    if not df["Gender"].isin(allowed_genders).all():
        raise ValueError(
            "Gender must be Male, Female, or Other."
        )

    # Validate marks and attendance
    numeric_columns = SUBJECTS + ["Attendance"]

    for col in numeric_columns:
        try:
            df[col] = pd.to_numeric(df[col], errors="raise")
        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"{col} must contain valid numbers."
            ) from exc

    # Reject missing numeric values
    if df[numeric_columns].isna().any().any():
        raise ValueError("Marks and attendance cannot be empty.")

    # Reject infinite values
    if not np.isfinite(
        df[numeric_columns].to_numpy(dtype=float)
    ).all():
        raise ValueError(
            "Marks and attendance must be finite numbers."
        )

    # Marks must be between 0 and 100
    if df[SUBJECTS].lt(0).any().any():
        raise ValueError("Marks cannot be negative.")

    if df[SUBJECTS].gt(100).any().any():
        raise ValueError("Marks cannot exceed 100.")

    # Attendance must be between 0 and 100
    if (
        df["Attendance"].lt(0).any()
        or df["Attendance"].gt(100).any()
    ):
        raise ValueError("Attendance must be between 0 and 100.")

    # Calculate total marks
    df["Total"] = df[SUBJECTS].sum(axis=1)

    # Calculate percentage
    df["Percentage"] = np.round(
        df["Total"] / len(SUBJECTS),
        2
    )

    # Pass only if every subject has at least 35 marks
    df["Result"] = np.where(
        df[SUBJECTS].ge(35).all(axis=1),
        "Pass",
        "Fail"
    )

    return df


def get_data():
    """Load and validate the saved student dataset."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Student dataset not found: {DATA_FILE}"
        )

    try:
        df = pd.read_csv(DATA_FILE)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(
            "The saved students.csv file is empty."
        ) from exc
    except pd.errors.ParserError as exc:
        raise ValueError(
            "The saved students.csv file has an invalid CSV format."
        ) from exc

    return analyze_data(df)


@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    error = ""

    # Handle CSV upload
    if request.method == "POST":
        file = request.files.get("dataset")

        if not file or not file.filename:
            error = "Please select a CSV file."

        elif not file.filename.lower().endswith(".csv"):
            error = "Please upload a CSV file."

        else:
            try:
                uploaded_df = pd.read_csv(file)
                validated_df = analyze_data(uploaded_df)

                # Save only after successful validation
                DATA_FILE.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

                validated_df[REQUIRED_COLUMNS].to_csv(
                    DATA_FILE,
                    index=False
                )

                message = "Dataset uploaded successfully!"

            except pd.errors.EmptyDataError:
                error = (
                    "Upload failed: CSV file is empty. "
                    "Please upload a CSV containing student data."
                )

            except pd.errors.ParserError:
                error = (
                    "Upload failed: Invalid CSV format. "
                    "Please check your file."
                )

            except (ValueError, UnicodeDecodeError) as exc:
                error = f"Upload failed: {exc}"

            except Exception:
                app.logger.exception("Unexpected CSV upload error")
                error = "Upload failed due to an unexpected error."

    # Load saved dataset
    try:
        df = get_data()

    except Exception:
        app.logger.exception("Unable to load student dataset")
        return (
            "Dataset error. Check data/students.csv "
            "and the terminal output for details.",
            500
        )

    # Search by student name or roll number
    search = request.args.get("search", "").strip()

    if search:
        mask = (
            df["Name"].str.contains(
                search,
                case=False,
                na=False,
                regex=False
            )
            |
            df["Roll_No"].str.contains(
                search,
                case=False,
                na=False,
                regex=False
            )
        )
        visible_students = df[mask]
    else:
        visible_students = df

    # Dashboard metrics
    total_students = len(df)

    average_percentage = (
        round(df["Percentage"].mean(), 2)
        if total_students else 0
    )

    pass_count = int((df["Result"] == "Pass").sum())
    fail_count = total_students - pass_count

    pass_percentage = (
        round(pass_count / total_students * 100, 2)
        if total_students else 0
    )

    # Top five students
    top_students = (
        df.sort_values(
            ["Percentage", "Name"],
            ascending=[False, True]
        )
        .head(5)
        .to_dict("records")
    )

    # Average marks by subject
    subject_averages = df[SUBJECTS].mean().round(2).to_dict()

    return render_template(
        "index.html",
        total_students=total_students,
        average_percentage=average_percentage,
        pass_percentage=pass_percentage,
        pass_count=pass_count,
        fail_count=fail_count,
        top_students=top_students,
        subject_averages=subject_averages,
        students=visible_students.to_dict("records"),
        message=message,
        error=error,
        search=search
    )


@app.route("/download")
def download_report():
    """Download analyzed student data as CSV."""

    try:
        df = get_data()

        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)

        return send_file(
            output,
            mimetype="text/csv",
            as_attachment=True,
            download_name="student_performance_report.csv"
        )

    except Exception:
        app.logger.exception("Unable to generate student report")
        return "Unable to generate the report.", 500


@app.errorhandler(413)
def file_too_large(error):
    return (
        "Upload failed: File size exceeds 5 MB. "
        "Please upload a smaller CSV file.",
        413
    )


if __name__ == "__main__":
    app.run(debug=True)
