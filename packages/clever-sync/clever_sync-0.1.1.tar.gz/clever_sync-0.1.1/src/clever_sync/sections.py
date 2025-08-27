from oneroster_api import Classes, Enrollments


def build_sections_data(
    enrollments: list[Enrollments], classes: list[Classes], teachers: list
) -> dict:
    return [
        build_section_entry(class_data, enrollments, teachers) for class_data in classes
    ]


def build_section_entry(
    class_data: Classes, enrollments_list: list[Enrollments], teachers: list
) -> dict:
    enrollment = get_enrollment(enrollments_list, class_data.sourced_id)
    return {
        "School_id": get_school_id(enrollment.user, teachers),
        "Section_id": class_data.sourced_id,
        "Teacher_id": enrollment.user.split("F")[-1],
        "Course_name": class_data.title,
        "Course_number": class_data.course,
        "Section_number": class_data.class_code,
        "Subject": class_data.subjects,
        "Term_start": enrollment.begin_date,
        "Term_end": enrollment.end_date,
        "Period": class_data.periods,
    }


def get_enrollment(
    enrollments_list: list[Enrollments], class_id: str | int
) -> Enrollments | None:
    for item in enrollments_list:
        if item.role == "teacher" and item.class_id == class_id:
            return item
    print(f"Item {class_id} not found in list")
    return None


def get_school_id(teacher_id: str, teacher_list: list) -> str | None:
    for teacher in teacher_list:
        # print(teacher["Teacher_number"])
        if teacher["Teacher_number"] == teacher_id:
            return teacher["School_id"]
    return None
