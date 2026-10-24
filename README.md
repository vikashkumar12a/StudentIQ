# Student Performance Analyzer

A Python-based student analytics web application built using Flask, Pandas, and NumPy. It helps analyze student performance through marks, attendance, percentages, and pass/fail results.

## Features

* Upload student data using CSV files.
* Validate uploaded data and required columns.
* Analyze subject marks and attendance.
* Calculate total marks and percentages.
* Determine pass/fail status.
* Handle missing, duplicate, and invalid data.
* Display analytics through a web dashboard.
* Run automated tests using pytest.

## Tech Stack

* Python
* Flask
* Pandas
* NumPy
* HTML, CSS, JavaScript
* pytest and pytest-cov

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd "Student Performance Analyzer"
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

Windows Command Prompt:

```cmd
venv\Scripts\activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Run the Application

```bash
python app.py
```

Open the local URL displayed in your terminal.

## Run Tests

Run the complete test suite:

```bash
python -m pytest -v
```

Run tests with coverage:

```bash
python -m pytest --cov=app --cov-report=term-missing
```

## Project Structure

```text
Student Performance Analyzer/
├── app.py
├── data/
├── static/
│   ├── script.js
│   └── style.css
├── templates/
│   └── index.html
├── tests/
│   └── test_app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Future Improvements

* More advanced student performance analytics.
* Improved reporting and data visualization.
* Additional automated tests.
* Secure multi-user support.

## Disclaimer

This project is intended for learning, data analysis, and portfolio demonstration.
