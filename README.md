# Student Performance Analysis System — Modern Dark / Light dashboard

A polished Streamlit application for analysing student marks. It includes a modern navy dashboard, a Dark/Light appearance switch, a dedicated CSV upload area, data cleaning, grades, ranking, charts, descriptive statistics, and PDF/CSV exports.

## Run on Windows

1. Open this project folder in VS Code.
2. Open a terminal in that folder.
3. Install the libraries:

   ```powershell
   py -m pip install -r requirements.txt
   ```

4. Start the app:

   ```powershell
   py -m streamlit run app.py
   ```

5. Open the local address printed in the terminal, usually `http://localhost:8501`.

Python 3.10 or newer is recommended.

## Quick start with sample data

`sample_100_students.csv` contains 100 generated student records that you can upload straight away to try every screen.

## Upload your own CSV

Use **Upload student data → Choose a CSV file** in the sidebar. Uploading a file automatically switches **Use demo dataset** off, so your file is analysed immediately (you can still switch the demo back on at any time).

A recommended header is:

```csv
Student_ID,Name,Math,Science,English,Computer,Attendance
STU001,Aarav Patel,85,90,78,92,95
STU002,Diya Shah,92,88,95,96,98
```

The app accepts student ID and name columns with flexible common header names (`Roll No`, `Student Name`, `Full Name`, `USN`, …). If an ID or name column is missing, one is generated without clashing with existing values.

### How marks are interpreted

- Every numeric column is treated as a subject **except** known data-only columns: attendance, total, percentage, average, aggregate, rank, serial/number, semester, class, section, grade, result and status. These stay visible as data but never affect the subject average.
- Subject scores should be numeric and between 0 and 100. Percent signs are removed automatically.
- Marks outside 0–100 are treated as missing and filled with the subject median.
- Duplicate student IDs are removed, keeping the first record.
- Attendance is shown as a data field and used for the attendance scatter plot, but is excluded from the subject average.
- If no usable numeric subject column exists, the app stops with a clear message instead of showing an empty dashboard.

## Features

- Dark and Light theme switch that also re-styles Streamlit's own widgets
- CSV upload and data source indicator
- Data cleaning and duplicate ID handling
- Subject averages, class average, highest average and pass rate
- Grade calculation (A+, A, B, C, D, F)
- Student ranking with search (literal text, not regex) and grade filters
- Dedicated Charts section with subject averages, grade distribution, overall average histogram, subject score boxplots, and an attendance-vs-average scatter plot when attendance is available
- Dedicated Data Cleaning section with original file preview, cleaning summary, duplicate/invalid-value indicators, missing-value report, cleaned preview, and cleaned CSV download
- Descriptive statistics
- PDF report (metrics, subject averages, chart, top 20 ranking) and CSV exports
- Responsive layout: KPI cards go two-up and side-by-side panels stack on narrow screens and split views

## Grade rules

- A+: 90–100
- A: 80–89
- B: 70–79
- C: 60–69
- D: 50–59
- F: below 50

Pass criterion: average score of at least 35%.

## Project files

| File | Purpose |
| --- | --- |
| `app.py` | The complete Streamlit application |
| `requirements.txt` | Python dependencies |
| `sample_100_students.csv` | Demo data for a quick trial |
| `.streamlit/config.toml` | Pins Streamlit's base theme so the dashboard looks identical on every machine (instead of following the operating-system light/dark setting) |
