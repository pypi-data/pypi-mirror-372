from oneroster_api import Enrollments


def build_enrollment_data(
    enrollments_list: list[Enrollments], sections_data: list[dict]
) -> list[dict]:
    return [
        {
            "School_id": get_school_id(sections_data, enrollment.class_id),
            "Section_id": enrollment.class_id,
            "Student_id": int(enrollment.user.split("S")[-1]),
        }
        for enrollment in enrollments_list
        if enrollment.role == "student"
    ]


def get_school_id(sections_data: list[dict], section_id: int) -> str | None:
    for section in sections_data:
        if section["Section_id"] == section_id:
            return section["School_id"]
    return None
