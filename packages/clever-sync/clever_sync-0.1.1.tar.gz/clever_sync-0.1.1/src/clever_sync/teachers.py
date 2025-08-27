import csv
import subprocess
from pathlib import Path

from oneroster_api import Users

building_map = {
    "A3700.1": "A3700.1",
    "A3700.2": "A3700.2",
    "A3700.3": "A3700.3",
    "A3700.4": "A3700.1",
}


def build_teacher_data(users_list: list[Users]) -> list[dict]:
    user_data = get_gam_user_data()
    teachers = [
        {
            "School_id": get_building_id(user_data, teacher.email),
            "Teacher_id": teacher.identifier,
            "Teacher_number": teacher.sourced_id,
            "State_id": teacher.state_id,
            "First_name": teacher.first_name,
            "Last_name": teacher.last_name,
            "Teacher_email": teacher.email.lower(),
            "Username": teacher.email.split("@")[0].lower(),
        }
        for teacher in users_list
        if teacher.role == "teacher" and teacher.email
    ]
    return [
        teacher
        for teacher in teachers
        if teacher["School_id"] and teacher["School_id"].strip()
    ]


def get_gam_user_data():
    cmd = ["gam", "print", "users", "fields", "locations"]
    process = subprocess.run(cmd, capture_output=True, text=True, check=True)
    reader = csv.DictReader(process.stdout)
    user_data_path = Path("data/import/users.csv")
    with open(user_data_path, "w") as file:
        file.write(process.stdout)
    with open(user_data_path, "r") as file:
        reader = csv.DictReader(file)
        return [
            {"email": row["primaryEmail"], "building_id": row["locations.0.buildingId"]}
            for row in reader
        ]


def get_building_id(user_list: list[dict], email: str) -> str | None:
    for user in user_list:
        if user["email"].lower().strip() == email.lower().strip():
            if user["building_id"] in building_map.keys():
                return building_map[user["building_id"]]

    return None
