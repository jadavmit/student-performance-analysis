import io
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# ------------------------------ Column aliases ------------------------------
# Common header names that identify the student name column (checked in order).
NAME_ALIASES = (
    "name",
    "student name",
    "student_name",
    "studentname",
    "full name",
    "fullname",
    "student",
)
# Common header names that identify the student ID column (checked in order).
ID_ALIASES = (
    "student_id",
    "student id",
    "studentid",
    "id",
    "roll no",
    "roll_no",
    "roll number",
    "roll_number",
    "rollnumber",
    "reg no",
    "reg_no",
    "registration no",
    "admission no",
    "adm no",
    "enrollment no",
    "enrolment no",
    "usn",
    "gr no",
)
# Columns that are displayed as extra data but never counted as subject marks.
ATTENDANCE_ALIASES = {
    "attendance",
    "attendance %",
    "attendance (%)",
    "attendance_percent",
    "attendance percentage",
    "attendance_percentage",
    "attendence",
    "attendence %",
    "present %",
    "present percentage",
    "present_percentage",
}
# Aggregate / metadata columns that must not be treated as subject marks.
NON_SUBJECT_ALIASES = {
    "total",
    "total marks",
    "total_marks",
    "total marks obtained",
    "marks obtained",
    "marks_obtained",
    "grand total",
    "grand_total",
    "total score",
    "total_score",
    "sum",
    "sum of marks",
    "percentage",
    "percent",
    "overall",
    "overall percentage",
    "overall marks",
    "overall_marks",
    "overall score",
    "aggregate",
    "aggregate marks",
    "avg",
    "avg marks",
    "average",
    "average marks",
    "mean",
    "rank",
    "ranking",
    "class rank",
    "position",
    "position in class",
    "sr no",
    "sr_no",
    "s no",
    "s_no",
    "s.no",
    "sno",
    "serial",
    "serial no",
    "serial_no",
    "no",
    "index",
    "sem",
    "semester",
    "class",
    "section",
    "batch",
    "division",
    "term",
    "grade",
    "result",
    "status",
}

st.set_page_config(
    page_title="Student Performance Analytics",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------ Theme and layout ------------------------------
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"

with st.sidebar:
    st.markdown("# Workspace")
    st.caption("Student performance analytics")
    theme_mode = st.radio(
        "Appearance",
        options=["Dark", "Light"],
        horizontal=True,
        index=0 if st.session_state.theme_mode == "Dark" else 1,
        help="Switch between dark and light dashboard themes.",
    )
    st.session_state.theme_mode = theme_mode

is_dark = theme_mode == "Dark"
if is_dark:
    theme = {
        "page": "#080F1F",
        "panel": "#101B31",
        "panel2": "#15233D",
        "sidebar": "#0B1427",
        "text": "#E8EEF9",
        "muted": "#9BAAC4",
        "border": "#263752",
        "blue": "#4F8CFF",
        "teal": "#2DD4BF",
        "chart_grid": "#2A3A55",
        "chart_text": "#D9E3F5",
        "table_head": "#1D3760",
    }
else:
    theme = {
        "page": "#F3F6FC",
        "panel": "#FFFFFF",
        "panel2": "#EAF0FA",
        "sidebar": "#FFFFFF",
        "text": "#15223B",
        "muted": "#60708C",
        "border": "#DCE5F2",
        "blue": "#245FE5",
        "teal": "#078A83",
        "chart_grid": "#DCE5F2",
        "chart_text": "#27364F",
        "table_head": "#DCE9FF",
    }

# Streamlit's own widgets keep the light baseline theme from .streamlit/config.toml,
# so the colours below are explicit for both appearance modes.

sns.set_theme(
    style="whitegrid",
    rc={
        "axes.facecolor": theme["panel"],
        "figure.facecolor": theme["panel"],
        "grid.color": theme["chart_grid"],
        "text.color": theme["chart_text"],
        "axes.labelcolor": theme["chart_text"],
        "xtick.color": theme["chart_text"],
        "ytick.color": theme["chart_text"],
    },
)

st.markdown(
    f"""
    <style>
    :root {{
      --app-page: {theme['page']}; --app-panel: {theme['panel']};
      --app-panel2: {theme['panel2']}; --app-text: {theme['text']};
      --app-muted: {theme['muted']}; --app-border: {theme['border']};
      --app-blue: {theme['blue']}; --app-teal: {theme['teal']};
    }}
    .stApp {{ background: var(--app-page); color: var(--app-text); }}
    [data-testid="stSidebar"] {{ background: {theme['sidebar']}; border-right: 1px solid var(--app-border); }}
    [data-testid="stSidebar"] > div:first-child {{ padding-top: 1.2rem; }}
    .block-container {{ max-width: 1600px; padding-top: 1.4rem; padding-bottom: 2.5rem; }}
    h1, h2, h3, h4, p, label, span {{ color: inherit; }}
    [data-testid="stCaptionContainer"], .muted {{ color: var(--app-muted) !important; }}

    /* Text that Streamlit paints with its own theme colour */
    [data-testid="stSidebar"] {{ color: var(--app-text) !important; }}
    [data-testid="stSidebar"] * {{ color: inherit !important; }}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] *,
    [data-testid="stSidebar"] .upload-note,
    [data-testid="stSidebar"] .upload-note * {{ color: var(--app-muted) !important; }}
    [data-testid="stTabs"] [role="tab"] p {{ color: var(--app-text) !important; }}
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] p {{ color: var(--app-blue) !important; }}
    [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{ color: var(--app-text) !important; }}
    [data-testid="stHeader"] {{ background: var(--app-page) !important; }}
    [data-testid="stHeader"] * {{ color: var(--app-muted) !important; }}
    [data-testid="stToolbar"] {{ right: .5rem; }}

    /* Native widgets follow the dashboard palette instead of the light baseline */
    div.stButton > button, div.stDownloadButton > button,
    [data-testid="stFormSubmitButton"] button {{
      background: var(--app-panel2) !important; color: var(--app-text) !important;
      border: 1px solid var(--app-border) !important; border-radius: 10px; font-weight: 700;
    }}
    div.stButton > button:hover, div.stDownloadButton > button:hover {{
      color: var(--app-blue) !important; border-color: var(--app-blue) !important;
    }}
    div.stDownloadButton > button {{ width: 100%; }}
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea {{
      background: var(--app-panel) !important; color: var(--app-text) !important;
      border: 1px solid var(--app-border) !important;
    }}
    [data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder {{
      color: var(--app-muted) !important;
    }}
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{
      background: var(--app-panel) !important; border-color: var(--app-border) !important;
    }}
    [data-testid="stMultiSelect"] div[data-baseweb="select"] input,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] span,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] div {{
      color: var(--app-text) !important;
    }}
    [data-testid="stMultiSelect"] [data-baseweb="tag"] {{
      background: rgba(79,140,255,.18) !important; color: var(--app-text) !important;
    }}
    [data-baseweb="popover"], [data-baseweb="menu"] {{ background: var(--app-panel) !important; }}
    [data-baseweb="popover"] li, [data-baseweb="menu"] li {{ color: var(--app-text) !important; }}

    .hero {{
      padding: 1.8rem 2rem; border-radius: 22px; margin-bottom: 1.25rem;
      color: #F8FAFF; background: linear-gradient(115deg, #101C38 0%, #173D83 57%, #087F8C 100%);
      border: 1px solid #34558B; box-shadow: 0 16px 40px rgba(0,0,0,.16);
    }}
    .hero-kicker {{ text-transform: uppercase; letter-spacing: .16em; font-size: .72rem; font-weight: 800; color: #9BD9F7; margin-bottom: .65rem; }}
    .hero h1 {{ color: #FFFFFF !important; font-size: clamp(1.8rem, 3vw, 2.55rem); line-height: 1.15; margin: 0; font-weight: 800; letter-spacing: -.035em; }}
    .hero p {{ color: #D8E6FF !important; margin: .65rem 0 0; max-width: 800px; font-size: 1rem; }}
    .section-kicker {{ color: var(--app-muted); text-transform: uppercase; font-size: .72rem; font-weight: 800; letter-spacing: .14em; margin-bottom: .2rem; }}
    [data-testid="stMetric"] {{ background: var(--app-panel); border: 1px solid var(--app-border); border-radius: 17px; padding: 1rem 1.1rem; box-shadow: 0 5px 18px rgba(0,0,0,.05); }}
    [data-testid="stMetricLabel"] {{ color: var(--app-muted) !important; font-size: .85rem; font-weight: 650; }}
    [data-testid="stMetricLabel"] > div {{ white-space: normal !important; overflow: visible !important; text-overflow: clip !important; }}
    [data-testid="stMetricValue"] {{ color: var(--app-text) !important; font-weight: 800; }}
    [data-testid="stTabs"] button {{ font-weight: 750; }}
    [data-testid="stDataFrame"] {{ border: 1px solid var(--app-border); border-radius: 14px; overflow: hidden; }}
    [data-testid="stFileUploader"] {{ background: var(--app-panel); border: 1px dashed var(--app-blue); border-radius: 15px; padding: .55rem; }}
    [data-testid="stFileUploaderDropzone"] {{ background: var(--app-panel2); border-radius: 11px; }}
    [data-testid="stFileUploaderDropzone"] * {{ color: var(--app-text) !important; }}
    [data-testid="stFileUploaderDropzone"] button {{
      background: var(--app-blue) !important; color: #FFFFFF !important;
      border: none !important; border-radius: 9px; padding: .45rem .9rem;
    }}
    [data-testid="stFileUploaderDropzone"] button * {{ color: #FFFFFF !important; }}
    .upload-note {{ background: var(--app-panel2); border: 1px solid var(--app-border); border-radius: 12px; padding: .8rem .9rem; font-size: .84rem; color: var(--app-muted); }}
    .status-pill {{ display:inline-block; border-radius: 99px; padding: .28rem .62rem; font-size: .75rem; font-weight: 750; color: var(--app-teal); background: rgba(45,212,191,.13); border: 1px solid rgba(45,212,191,.38); }}
    hr {{ border-color: var(--app-border) !important; }}

    /* Two-up KPI cards whenever the viewport (or split view) is narrow */
    @media (max-width: 1300px) {{
      [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {{
        flex-wrap: wrap !important;
      }}
      [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > [data-testid="stColumn"],
      [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > [data-testid="column"] {{
        flex: 1 1 calc(50% - 1.1rem) !important;
        width: calc(50% - 1.1rem) !important;
        min-width: calc(50% - 1.1rem) !important;
      }}
    }}

    /* Stack side-by-side panels once there is not enough room for them */
    @media (max-width: 1100px) {{
      [data-testid="stHorizontalBlock"]:not(:has([data-testid="stMetric"])) {{
        flex-wrap: wrap !important;
      }}
      [data-testid="stHorizontalBlock"]:not(:has([data-testid="stMetric"])) > [data-testid="stColumn"],
      [data-testid="stHorizontalBlock"]:not(:has([data-testid="stMetric"])) > [data-testid="column"] {{
        flex: 1 1 100% !important;
        width: 100% !important;
        min-width: 100% !important;
      }}
    }}

    /* Mobile-friendly layout */
    @media (max-width: 768px) {{
      .block-container {{
        padding-top: .8rem !important;
        padding-bottom: 1.4rem !important;
        padding-left: .8rem !important;
        padding-right: .8rem !important;
      }}
      .hero {{
        padding: 1.15rem 1rem;
        border-radius: 16px;
        margin-bottom: .9rem;
      }}
      .hero-kicker {{
        font-size: .64rem;
        letter-spacing: .09em;
        line-height: 1.45;
      }}
      .hero h1 {{
        font-size: clamp(1.45rem, 7vw, 2rem);
        line-height: 1.16;
        overflow-wrap: anywhere;
      }}
      .hero p {{
        font-size: .9rem;
        line-height: 1.5;
      }}
      [data-testid="stHorizontalBlock"] {{
        gap: .65rem !important;
      }}
      [data-testid="stMetric"] {{
        padding: .75rem .8rem;
        border-radius: 13px;
      }}
      [data-testid="stMetricValue"] {{
        font-size: 1.35rem;
        overflow-wrap: anywhere;
      }}
      [data-testid="stTabs"] [role="tablist"] {{
        gap: .25rem;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        scrollbar-width: thin;
      }}
      [data-testid="stTabs"] button[role="tab"] {{
        flex: 0 0 auto !important;
        white-space: nowrap !important;
        padding-left: .65rem !important;
        padding-right: .65rem !important;
        font-size: .82rem !important;
      }}
      [data-testid="stDataFrame"], [data-testid="stTable"] {{
        max-width: 100% !important;
      }}
      [data-testid="stFileUploader"] {{
        padding: .35rem;
      }}
      div.stButton > button, div.stDownloadButton > button {{
        min-height: 2.75rem;
        white-space: normal;
      }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------ Demo data and cleaning ------------------------------
def sample_data():
    return pd.DataFrame(
        {
            "Student_ID": [f"STU{i:03d}" for i in range(1, 16)],
            "Name": [
                "Aarav Patel", "Diya Shah", "Vivaan Joshi", "Anaya Mehta", "Reyansh Desai",
                "Aadhya Trivedi", "Krish Parmar", "Ira Pandya", "Atharv Dave", "Sara Modi",
                "Kabir Rathod", "Myra Thakkar", "Arjun Solanki", "Kiara Vyas", "Dev Chauhan",
            ],
            "Math": [82, 94, 68, 88, 73, 96, 59, 91, 77, 84, 65, 89, 71, 98, 56],
            "Science": [78, 91, 72, 85, 69, 93, 61, 88, 81, 79, 70, 86, 74, 95, 60],
            "English": [86, 88, 75, 91, 72, 89, 66, 94, 78, 85, 73, 90, 80, 92, 64],
            "Computer": [91, 97, 70, 93, 81, 99, 64, 96, 85, 90, 72, 95, 78, 100, 62],
            "Attendance": [92, 98, 81, 95, 78, 99, 74, 96, 88, 91, 80, 94, 86, 100, 72],
        }
    )


def pick_column(columns, aliases, canonical):
    """Return the best matching column for a role, preferring the canonical name."""
    if canonical in columns:
        return canonical
    lowered = {str(column).lower(): column for column in columns}
    for alias in aliases:
        if alias in lowered:
            return lowered[alias]
    return None


def clean_data(raw):
    """Clean a raw dataframe and describe what was done to it."""
    df = raw.copy()
    df.columns = [str(column).strip() for column in df.columns]
    df = df.loc[:, ~pd.Index(df.columns).duplicated()]

    # --- student name / student id columns -----------------------------------
    name_col = pick_column(df.columns, NAME_ALIASES, "Name")
    id_col = pick_column(df.columns, ID_ALIASES, "Student_ID")

    generated_names = 0
    if name_col is None:
        df["Name"] = [f"Student {index + 1}" for index in range(len(df))]
        name_col = "Name"
        generated_names = len(df)
    elif name_col != "Name":
        # "Name" is not present, so renaming cannot create a duplicate column.
        df = df.rename(columns={name_col: "Name"})

    generated_ids = 0
    if id_col is None:
        df.insert(0, "Student_ID", [f"STU{index + 1:03d}" for index in range(len(df))])
        id_col = "Student_ID"
    elif id_col != "Student_ID":
        df = df.rename(columns={id_col: "Student_ID"})

    df = df.loc[:, ~pd.Index(df.columns).duplicated()]

    df["Name"] = (
        df["Name"].astype("string").str.strip().replace("", pd.NA).fillna("Unknown Student")
    )

    # Numeric ID columns become floats as soon as a cell is blank ("1.0"), so make
    # whole numbers look like plain integers again before converting to text.
    student_ids = df["Student_ID"]
    if pd.api.types.is_float_dtype(student_ids):
        whole_numbers = student_ids.dropna()
        if not whole_numbers.empty and whole_numbers.mod(1).eq(0).all():
            df["Student_ID"] = student_ids.astype("Int64")
    df["Student_ID"] = df["Student_ID"].astype("string").str.strip().replace("", pd.NA)

    # --- fill missing IDs with values that do not clash with existing IDs ----
    missing_ids = df["Student_ID"].isna()
    if missing_ids.any():
        used_ids = set(df["Student_ID"].dropna().tolist())
        counter = 1
        for position in df.index[missing_ids]:
            while f"STU{counter:03d}" in used_ids:
                counter += 1
            new_id = f"STU{counter:03d}"
            used_ids.add(new_id)
            df.at[position, "Student_ID"] = new_id
            generated_ids += 1

    # --- numeric conversion --------------------------------------------------
    numeric_columns = []
    for column in df.columns:
        if column in ["Name", "Student_ID"]:
            continue
        values = pd.to_numeric(
            df[column].astype(str).str.replace("%", "", regex=False).str.strip(),
            errors="coerce",
        )
        if values.notna().sum() > 0:
            df[column] = values
            numeric_columns.append(column)

    # --- classify the numeric columns ----------------------------------------
    attendance_col = None
    for column in numeric_columns:
        if str(column).lower() in ATTENDANCE_ALIASES:
            attendance_col = column
            break

    subjects = []
    for column in numeric_columns:
        if column == attendance_col:
            continue
        if str(column).lower() in NON_SUBJECT_ALIASES:
            continue
        subjects.append(column)

    if not subjects:
        raise ValueError(
            "No numeric subject marks found. Include at least one subject column with scores from 0 to 100."
        )

    # --- subject score validation --------------------------------------------
    invalid_score_cells = 0
    for column in subjects:
        invalid = (df[column] < 0) | (df[column] > 100)
        invalid_score_cells += int(invalid.sum())
        df.loc[invalid, column] = np.nan
        median = df[column].median() if df[column].notna().any() else 0
        df[column] = df[column].fillna(median)

    if attendance_col is not None:
        df[attendance_col] = df[attendance_col].clip(0, 100)

    # --- duplicate student IDs ------------------------------------------------
    before = len(df)
    df = df.drop_duplicates(subset=["Student_ID"], keep="first").reset_index(drop=True)
    removed_duplicates = before - len(df)

    return {
        "df": df,
        "subjects": subjects,
        "attendance_col": attendance_col,
        "removed_duplicates": removed_duplicates,
        "invalid_score_cells": invalid_score_cells,
        "generated_ids": generated_ids,
        "generated_names": generated_names,
    }


def grade(score):
    if score >= 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def chart_style(ax, horizontal=False):
    ax.set_facecolor(theme["panel"])
    ax.grid(axis="x" if horizontal else "y", color=theme["chart_grid"], alpha=0.75, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=theme["chart_text"], labelsize=9)
    ax.xaxis.label.set_color(theme["chart_text"])
    ax.yaxis.label.set_color(theme["chart_text"])
    for spine in ax.spines.values():
        spine.set_color(theme["border"])
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)


def make_subject_chart(means):
    fig, ax = plt.subplots(figsize=(8, 4.2), facecolor=theme["panel"])
    values = means.sort_values()
    bars = ax.barh(values.index, values.values, color=theme["blue"], height=0.62)
    ax.set_xlabel("Average marks (%)")
    ax.set_xlim(0, 110)
    chart_style(ax, horizontal=True)
    for bar, value in zip(bars, values.values):
        ax.text(
            value + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.1f}%",
            va="center",
            color=theme["chart_text"],
            fontsize=9,
        )
    fig.tight_layout()
    return fig


def png_dimensions(data):
    """Read the pixel size of a PNG image without extra dependencies."""
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")


def pdf_report(summary, ranked, means, chart_png):
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Student Performance Analysis Report", styles["Title"]),
        Paragraph(f"Generated {datetime.now().strftime('%d %B %Y, %I:%M %p')}", styles["Normal"]),
        Spacer(1, 5 * mm),
    ]

    overview_rows = [
        ["Metric", "Value"],
        ["Students analysed", str(summary["students"])],
        ["Class average", f"{summary['average']:.2f}%"],
        ["Highest average", f"{summary['highest']:.2f}%"],
        ["Pass rate", f"{summary['pass_rate']:.1f}%"],
        ["Subjects", str(summary["subjects"])],
    ]
    overview_table = Table(overview_rows, colWidths=[55 * mm, 45 * mm])
    overview_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172554")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([overview_table, Spacer(1, 5 * mm), Paragraph("Subject averages", styles["Heading2"])])

    subject_rows = [["Subject", "Average"]]
    subject_rows.extend([[str(subject), f"{average:.2f}%"] for subject, average in means.items()])
    subject_table = Table(subject_rows, colWidths=[65 * mm, 45 * mm])
    subject_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F766E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.extend([subject_table, Spacer(1, 5 * mm), Paragraph("Student ranking (top 20)", styles["Heading2"])])

    ranking_rows = [["Rank", "Student ID", "Student Name", "Average", "Grade", "Result"]]
    for _, student in ranked.head(20).iterrows():
        ranking_rows.append(
            [
                str(int(student["Rank"])),
                str(student["Student_ID"]),
                str(student["Name"]),
                f"{student['Average']:.2f}%",
                student["Grade"],
                student["Result"],
            ]
        )
    ranking_table = Table(
        ranking_rows,
        repeatRows=1,
        colWidths=[16 * mm, 30 * mm, 65 * mm, 27 * mm, 20 * mm, 25 * mm],
    )
    ranking_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#172554")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    # Keep the chart proportions and make sure it fits on the page.
    image_width = 235 * mm
    image_height = 100 * mm
    dimensions = png_dimensions(chart_png)
    if dimensions and dimensions[0]:
        image_height = image_width * dimensions[1] / dimensions[0]
        if image_height > 115 * mm:
            image_height = 115 * mm
            image_width = image_height * dimensions[0] / dimensions[1]

    story.extend(
        [
            ranking_table,
            Spacer(1, 5 * mm),
            Paragraph("Subject performance chart", styles["Heading2"]),
            Image(io.BytesIO(chart_png), width=image_width, height=image_height),
        ]
    )
    document.build(story)
    return buffer.getvalue()


# ------------------------------ Upload controls ------------------------------
with st.sidebar:
    st.divider()
    st.markdown("### Upload student data")
    st.caption("Import your own class marks to analyse them instantly.")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="CSV must contain at least one numeric subject score column from 0 to 100.",
        label_visibility="visible",
    )
    st.markdown(
        '<div class="upload-note"><b>Recommended columns</b><br>Student_ID, Name, Math, Science, English, Computer, Attendance</div>',
        unsafe_allow_html=True,
    )

    # Turn the demo dataset off automatically as soon as a file is uploaded.
    upload_signature = uploaded_file.name if uploaded_file is not None else None
    if st.session_state.get("upload_signature") != upload_signature:
        st.session_state["upload_signature"] = upload_signature
        if upload_signature is not None:
            st.session_state["demo_mode"] = False
    if "demo_mode" not in st.session_state:
        st.session_state["demo_mode"] = uploaded_file is None
    demo_mode = st.toggle("Use demo dataset", key="demo_mode")
    st.divider()
    st.markdown("### Grade scale")
    st.markdown("**A+** &nbsp; 90–100  \n**A** &nbsp; 80–89  \n**B** &nbsp; 70–79  \n**C** &nbsp; 60–69  \n**D** &nbsp; 50–59  \n**F** &nbsp; below 50", unsafe_allow_html=True)
    st.caption("Pass criterion: average score ≥ 35%.")

# ------------------------------ Process dataset ------------------------------
try:
    if uploaded_file is not None and not demo_mode:
        raw_data = pd.read_csv(uploaded_file)
        data_source = uploaded_file.name
    else:
        raw_data = sample_data()
        data_source = "Demo dataset"
    cleaning = clean_data(raw_data)
except Exception as error:
    st.error(f"Could not process this CSV: {error}")
    st.info("Upload a CSV with a student name and at least one numeric subject marks column (0–100).")
    st.stop()

df = cleaning["df"]
subjects = cleaning["subjects"]
attendance_col = cleaning["attendance_col"]
duplicate_count = cleaning["removed_duplicates"]

if uploaded_file is not None and demo_mode:
    st.info(
        f"**{uploaded_file.name}** is uploaded but the demo dataset is still active. "
        "Switch off *Use demo dataset* in the sidebar to analyse your file."
    )
elif uploaded_file is None and not demo_mode:
    st.info("No CSV file is uploaded, so the demo dataset is shown. Upload a file in the sidebar to analyse your own data.")

if df.empty:
    st.error("No usable student records were found in this file.")
    st.stop()

# ------------------------------ Calculations ------------------------------
df["Average"] = df[subjects].mean(axis=1).round(2)
df["Grade"] = df["Average"].apply(grade)
df["Result"] = np.where(df["Average"] >= 35, "Pass", "Needs Support")
ranked = df.sort_values(["Average", "Name"], ascending=[False, True]).reset_index(drop=True)
ranked["Rank"] = ranked["Average"].rank(method="min", ascending=False).astype(int)
means = df[subjects].mean().sort_values(ascending=False)
grade_order = ["A+", "A", "B", "C", "D", "F"]
grade_counts = df["Grade"].value_counts().reindex(grade_order, fill_value=0)
class_average = float(df["Average"].mean())
pass_rate = float((df["Average"] >= 35).mean() * 100)
summary = {
    "students": len(df),
    "average": class_average,
    "highest": float(df["Average"].max()),
    "pass_rate": pass_rate,
    "subjects": len(subjects),
}

# ------------------------------ Header and KPI cards ------------------------------
st.markdown(
    """
    <div class="hero">
      <div class="hero-kicker">Academic intelligence · Performance overview</div>
      <h1>Student Performance<br>Analysis System</h1>
      <p>Understand class results, compare subjects, discover learning trends and export a clear report from one workspace.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

source_col, count_col = st.columns([3, 1])
with source_col:
    st.markdown(f'<span class="status-pill">DATA READY</span> &nbsp; <span class="muted">Source: {data_source}</span>', unsafe_allow_html=True)
with count_col:
    st.markdown(f'<p style="text-align:right;color:{theme["muted"]};margin-top:.2rem">{len(df):,} records · {len(subjects)} subjects</p>', unsafe_allow_html=True)

metric_columns = st.columns(4, gap="medium")
metric_columns[0].metric("Students analysed", f"{len(df):,}")
metric_columns[1].metric("Class average", f"{class_average:.1f}%")
metric_columns[2].metric("Pass rate", f"{pass_rate:.1f}%")
metric_columns[3].metric("Highest average", f"{df['Average'].max():.1f}%")

if duplicate_count:
    st.info(f"Data cleaning removed {duplicate_count} duplicate student ID record(s). Invalid marks were treated as missing and filled with the subject median.")

# ------------------------------ Main dashboard tabs ------------------------------
overview_tab, charts_tab, cleaning_tab, ranking_tab, explore_tab, reports_tab = st.tabs(
    ["Overview", "Charts", "Data cleaning", "Student ranking", "Statistics", "Reports & exports"]
)

with overview_tab:
    st.markdown('<div class="section-kicker">Class insights</div>', unsafe_allow_html=True)
    st.subheader("Performance at a glance")
    chart_left, chart_right = st.columns([1.25, 1], gap="large")

    with chart_left:
        st.markdown("#### Average marks by subject")
        subject_fig = make_subject_chart(means)
        st.pyplot(subject_fig, width="stretch")
        plt.close(subject_fig)
        st.caption("Compare average marks across all detected subject columns.")

    with chart_right:
        st.markdown("#### Students by grade")
        fig, ax = plt.subplots(figsize=(6.5, 4.2), facecolor=theme["panel"])
        grade_palette = ["#2DD4BF", "#34D399", "#A3E635", "#FBBF24", "#FB923C", "#F87171"]
        bars = ax.bar(grade_counts.index, grade_counts.values, color=grade_palette, width=0.68)
        ax.set_ylabel("Number of students")
        ax.set_ylim(0, max(1, int(grade_counts.max()) + 2))
        chart_style(ax)
        for bar, value in zip(bars, grade_counts.values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + 0.08,
                str(int(value)),
                ha="center",
                color=theme["chart_text"],
                fontsize=9,
            )
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)
        st.caption("Number of students in each grade band.")

    st.divider()
    top_col, insight_col = st.columns([1.2, 1], gap="large")
    with top_col:
        st.markdown("#### Top 5 students")
        top_students = ranked.head(5)[["Rank", "Student_ID", "Name", "Average", "Grade"]].copy()
        top_students["Average"] = top_students["Average"].map(lambda value: f"{value:.2f}%")
        st.dataframe(top_students, width="stretch", hide_index=True)
    with insight_col:
        st.markdown("#### Key observations")
        st.success(f"Strongest subject: {means.index[0]} — {means.iloc[0]:.1f}% average.")
        if len(means) > 1:
            st.info(f"Subject needing the most attention: {means.index[-1]} — {means.iloc[-1]:.1f}% average.")
        below_50 = int((df["Average"] < 50).sum())
        if below_50:
            st.warning(f"{below_50} student(s) have an overall average below 50%.")
        else:
            st.success("No student has an overall average below 50%.")

with charts_tab:
    st.markdown('<div class="section-kicker">Visual analytics</div>', unsafe_allow_html=True)
    st.subheader("Charts & performance patterns")
    st.caption("A dedicated chart workspace with different views of the selected student dataset.")

    chart_row_one_left, chart_row_one_right = st.columns(2, gap="large")
    with chart_row_one_left:
        st.markdown("#### 1. Average marks by subject")
        chart_fig = make_subject_chart(means)
        st.pyplot(chart_fig, width="stretch")
        plt.close(chart_fig)

    with chart_row_one_right:
        st.markdown("#### 2. Grade distribution")
        grade_fig, grade_ax = plt.subplots(figsize=(7, 4.2), facecolor=theme["panel"])
        nonzero_grades = grade_counts[grade_counts > 0]
        grade_palette = ["#2DD4BF", "#34D399", "#A3E635", "#FBBF24", "#FB923C", "#F87171"]
        wedges, labels, percentages = grade_ax.pie(
            nonzero_grades.values,
            labels=nonzero_grades.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=grade_palette[:len(nonzero_grades)],
            wedgeprops={"width": 0.42, "edgecolor": theme["panel"]},
            textprops={"color": theme["chart_text"], "fontsize": 9},
        )
        grade_ax.set_facecolor(theme["panel"])
        grade_ax.axis("equal")
        grade_fig.tight_layout()
        st.pyplot(grade_fig, width="stretch")
        plt.close(grade_fig)

    chart_row_two_left, chart_row_two_right = st.columns(2, gap="large")
    with chart_row_two_left:
        st.markdown("#### 3. Overall average distribution")
        hist_fig, hist_ax = plt.subplots(figsize=(7, 4.2), facecolor=theme["panel"])
        hist_ax.hist(df["Average"], bins=min(10, max(5, int(np.sqrt(len(df))))), color=theme["blue"], edgecolor=theme["panel"], alpha=0.92)
        hist_ax.set_xlabel("Overall average (%)")
        hist_ax.set_ylabel("Number of students")
        chart_style(hist_ax)
        hist_fig.tight_layout()
        st.pyplot(hist_fig, width="stretch")
        plt.close(hist_fig)

    with chart_row_two_right:
        st.markdown("#### 4. Subject score spread")
        box_fig, box_ax = plt.subplots(figsize=(7, 4.2), facecolor=theme["panel"])
        box_data = [df[subject].dropna().values for subject in subjects]
        boxplot_options = {
            "patch_artist": True,
            "medianprops": {"color": theme["teal"], "linewidth": 2},
        }
        try:
            boxplot = box_ax.boxplot(box_data, tick_labels=subjects, **boxplot_options)
        except TypeError:
            boxplot = box_ax.boxplot(box_data, labels=subjects, **boxplot_options)
        for patch in boxplot["boxes"]:
            patch.set_facecolor(theme["blue"])
            patch.set_alpha(0.62)
        box_ax.set_ylabel("Marks (%)")
        box_ax.tick_params(axis="x", labelrotation=20)
        chart_style(box_ax)
        box_fig.tight_layout()
        st.pyplot(box_fig, width="stretch")
        plt.close(box_fig)

    if attendance_col is not None:
        st.markdown("#### Bonus: Attendance vs overall average")
        scatter_fig, scatter_ax = plt.subplots(figsize=(10, 4.3), facecolor=theme["panel"])
        scatter_ax.scatter(df[attendance_col], df["Average"], color=theme["teal"], alpha=0.8, edgecolors=theme["panel"], s=48)
        scatter_ax.set_xlabel("Attendance (%)")
        scatter_ax.set_ylabel("Overall average (%)")
        chart_style(scatter_ax)
        scatter_fig.tight_layout()
        st.pyplot(scatter_fig, width="stretch")
        plt.close(scatter_fig)
        st.caption("This scatter plot helps explore whether attendance and academic averages move together.")

with cleaning_tab:
    st.markdown('<div class="section-kicker">Data quality workspace</div>', unsafe_allow_html=True)
    st.subheader("Data cleaning & validation")
    st.write("Review the original uploaded data, see the cleaning summary, and download the cleaned dataset.")

    raw_rows = len(raw_data)
    raw_columns = len(raw_data.columns)
    raw_missing_cells = int(raw_data.isna().sum().sum())
    cleaned_rows = len(df)
    removed_rows = max(0, raw_rows - cleaned_rows)
    invalid_score_cells = cleaning["invalid_score_cells"]

    clean_metrics = st.columns(4, gap="medium")
    clean_metrics[0].metric("Input rows", f"{raw_rows:,}")
    clean_metrics[1].metric("Cleaned rows", f"{cleaned_rows:,}")
    clean_metrics[2].metric("Duplicate IDs removed", f"{duplicate_count:,}")
    clean_metrics[3].metric("Blank cells in source", f"{raw_missing_cells:,}")

    st.markdown("#### Cleaning operations applied")
    st.markdown(
        "- Trimmed spaces from column names and student names.\n"
        "- Standardized common student name and ID column labels.\n"
        "- Generated student names or IDs when those columns were missing.\n"
        "- Converted numeric score columns and removed percent signs before conversion.\n"
        "- Treated scores outside the 0–100 range as missing values.\n"
        "- Filled missing subject marks with the median for that subject.\n"
        "- Kept attendance and aggregate columns (total, percentage, rank, …) as data fields only.\n"
        "- Removed duplicate student IDs, keeping the first record."
    )
    if invalid_score_cells:
        st.warning(f"Found {invalid_score_cells:,} numeric score value(s) outside the 0–100 range in the source file. These were treated as missing and filled during cleaning where applicable.")
    if removed_rows:
        st.info(f"The cleaned dataset contains {removed_rows:,} fewer row(s) than the source dataset.")
    else:
        st.success("No duplicate student ID rows were removed from this dataset.")
    if cleaning["generated_ids"] or cleaning["generated_names"]:
        st.info(
            f"Generated {cleaning['generated_names']:,} student name(s) and "
            f"{cleaning['generated_ids']:,} student ID(s) for records that were missing them."
        )

    st.markdown("#### Original file preview")
    st.dataframe(raw_data.head(20), width="stretch", hide_index=True)
    st.caption(f"Showing up to 20 of {raw_rows:,} original rows from {data_source}.")

    st.markdown("#### Missing values by source column")
    if raw_columns:
        missing_report = pd.DataFrame({
            "Column": [str(raw_data.columns[index]) for index in range(raw_columns)],
            "Missing values": [int(raw_data.iloc[:, index].isna().sum()) for index in range(raw_columns)],
            "Missing (%)": [round(float(raw_data.iloc[:, index].isna().mean() * 100), 2) if raw_rows else 0.0 for index in range(raw_columns)],
        }).sort_values("Missing values", ascending=False)
    else:
        missing_report = pd.DataFrame(columns=["Column", "Missing values", "Missing (%)"])
    st.dataframe(missing_report, width="stretch", hide_index=True)

    st.markdown("#### Cleaned data preview")
    st.dataframe(df.head(25), width="stretch", hide_index=True)
    st.download_button(
        "Download cleaned dataset (CSV)",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="cleaned_student_data.csv",
        mime="text/csv",
        width="stretch",
    )

with ranking_tab:
    st.markdown('<div class="section-kicker">Leaderboard</div>', unsafe_allow_html=True)
    st.subheader("Find and compare students")
    search_col, grade_col = st.columns([1.4, 1])
    with search_col:
        search_text = st.text_input("Search by student name or ID", placeholder="Try Aarav or STU001")
    with grade_col:
        selected_grades = st.multiselect("Filter by grade", grade_order, default=[])

    filtered = ranked.copy()
    if search_text.strip():
        needle = search_text.strip()
        filtered = filtered[
            filtered["Name"].str.contains(needle, case=False, na=False, regex=False)
            | filtered["Student_ID"].astype(str).str.contains(needle, case=False, na=False, regex=False)
        ]
    if selected_grades:
        filtered = filtered[filtered["Grade"].isin(selected_grades)]
    ranking_columns = ["Rank", "Student_ID", "Name"] + subjects + ["Average", "Grade", "Result"]
    st.caption(f"Showing {len(filtered)} of {len(ranked)} students.")
    st.dataframe(filtered[ranking_columns], width="stretch", hide_index=True)
    st.download_button(
        "Download filtered ranking (CSV)",
        data=filtered[ranking_columns].to_csv(index=False).encode("utf-8-sig"),
        file_name="student_ranking.csv",
        mime="text/csv",
        width="stretch",
    )

with explore_tab:
    st.markdown('<div class="section-kicker">Class statistics</div>', unsafe_allow_html=True)
    st.subheader("Descriptive statistics")
    st.caption("Explore the distribution of marks and download a summary of the cleaned dataset.")
    st.markdown("#### Descriptive statistics")
    statistics = df[subjects + ["Average"]].describe().T.round(2)
    st.dataframe(statistics, width="stretch")
    download_left, download_right = st.columns(2)
    with download_left:
        st.download_button(
            "Download cleaned data (CSV)",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="cleaned_student_data.csv",
            mime="text/csv",
            width="stretch",
        )
    with download_right:
        st.download_button(
            "Download descriptive statistics (CSV)",
            data=statistics.to_csv().encode("utf-8-sig"),
            file_name="student_statistics.csv",
            mime="text/csv",
            width="stretch",
        )

with reports_tab:
    st.markdown('<div class="section-kicker">Export centre</div>', unsafe_allow_html=True)
    st.subheader("Download your analysis")
    st.write("Generate a PDF summary with key metrics, subject averages, a performance chart and the top 20 students.")
    report_fig = make_subject_chart(means)
    chart_buffer = io.BytesIO()
    report_fig.savefig(chart_buffer, format="png", dpi=170, bbox_inches="tight", facecolor=theme["panel"])
    plt.close(report_fig)
    pdf_bytes = pdf_report(summary, ranked, means, chart_buffer.getvalue())

    pdf_col, csv_col = st.columns(2, gap="medium")
    with pdf_col:
        st.markdown("#### PDF report")
        st.caption("Summary metrics, subject averages, chart and top 20 ranking.")
        st.download_button(
            "Download PDF analysis report",
            data=pdf_bytes,
            file_name="student_performance_report.pdf",
            mime="application/pdf",
            width="stretch",
        )
    with csv_col:
        st.markdown("#### Full analysis CSV")
        st.caption("All cleaned records with average, grade and result columns.")
        st.download_button(
            "Download full analysis (CSV)",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name="student_performance_analysis.csv",
            mime="text/csv",
            width="stretch",
        )

st.divider()
st.caption("Built with Python, Pandas, NumPy, Matplotlib, Seaborn, Streamlit and ReportLab.")
