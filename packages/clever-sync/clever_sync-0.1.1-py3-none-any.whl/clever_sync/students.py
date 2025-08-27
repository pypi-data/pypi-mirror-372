import re

from oneroster_api import Demographics, Users


def build_student_data(
    user_list: list[Users], enrollment_data: list[dict], demographic_data: list[dict]
) -> list[dict]:
    return [
        student_data(user, enrollment_data, demographic_data)
        for user in user_list
        if user.role == "student"
    ]


def student_data(
    student: Users, enrollment_data: list[dict], demographic_data: list[Demographics]
) -> dict:
    student_email = check_email(
        student.email, student.preferred_first_name, student.preferred_last_name
    )
    return {
        "School_id": get_school_id_from_enrollment(enrollment_data, student.identifier),
        "Student_id": student.identifier,
        "Student_number": student.sourced_id,
        "State_id": student.state_id,
        "Last_name": student.last_name,
        "Middle_name": student.middle_name,
        "First_name": student.first_name,
        "Preferred_last_name": student.preferred_last_name,
        "Preferred_first_name": student.preferred_first_name,
        "Grade": student.grades,
        "DOB": get_date_of_birth(demographic_data, student.sourced_id),
        "Student_email": student_email,
        "Username": student_email.split("@")[0],
    }


def get_date_of_birth(demographics_data: list[Demographics], student_id) -> str | None:
    for demographics in demographics_data:
        if demographics.sourced_id == student_id:
            return demographics.birth_date
    return None


def check_email(email: str, firstname: str, lastname: str) -> str:
    if email == "" or email is None:
        email = make_student_email(firstname, lastname)
    return email.lower()


def clean_email(email: str) -> str:
    """Remove specific characters from email str."""
    return re.sub(r"[^a-zA-Z0-9.@]", "", email).lower()


def make_student_email(firstname: str, lastname: str) -> None:
    """Creates an email in firstnamelastname@school.org pattern."""
    email = f"{firstname}{lastname}@mydasa.org"
    return clean_email(email)


def get_school_id_from_enrollment(
    enrollment_data: list[dict], student_id
) -> str | None:
    for enrollment in enrollment_data:
        if enrollment["Student_id"] == student_id:
            return enrollment["School_id"]
    return None
