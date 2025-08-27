import csv
from pathlib import Path

from .enrollments import build_enrollment_data
from .sections import build_sections_data
from .students import build_student_data
from .teachers import build_teacher_data

__all__ = [
    "build_sections_data",
    "build_teacher_data",
    "build_student_data",
    "build_enrollment_data",
    "build_student_data",
]


def build_clever_sheets(oneroster_data: list[dict]) -> dict:
    teachers_data = build_teacher_data(oneroster_data["users"])
    sections_data = build_sections_data(
        oneroster_data["enrollments"], oneroster_data["classes"], teachers_data
    )
    enrollments_data = build_enrollment_data(
        oneroster_data["enrollments"], sections_data
    )
    students_data = build_student_data(
        oneroster_data["users"], enrollments_data, oneroster_data["demographics"]
    )
    return {
        "teachers": teachers_data,
        "sections": sections_data,
        "enrollments": enrollments_data,
        "students": students_data,
    }


def export_clever_sheets(clever_sheets: dict, clever_directory: Path = Path()) -> None:
    for sheet_name, data in clever_sheets.items():
        file_path = clever_directory / f"{sheet_name}.csv"
        keys = data[0].keys()
        with open(file_path, "w", encoding="utf8", newline="") as file:
            writer = csv.DictWriter(file, keys)
            writer.writeheader()
            writer.writerows(data)
