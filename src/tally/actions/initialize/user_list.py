import tkinter
from tkinter import filedialog
from typing import List
from pydantic import BaseModel
import csv


def prompt_user_list() -> str:
    print("Use the pop-up file explorer to select the user list for the challenge")

    root = tkinter.Tk()
    # Prevents the tkinter window from appearing
    root.withdraw()

    path = filedialog.askopenfilename(
        title="Select the user table",
        filetypes=[("CSV files", "*.csv")],
    )

    root.destroy()

    if path:
        print(f"Selected file: {path}")

    return path


class UserRow(BaseModel):
    team_id: str
    team_name: str
    user_name: str
    user_link: str

    def get_user_id(self) -> str:
        return self.user_link.split("/")[-1]

    def is_incomplete(self) -> bool:
        return (
            not self.team_id
            or not self.team_name
            or not self.user_name
            or not self.user_link
        )


def parse_user_list(user_list_path: str) -> List[UserRow]:
    with open(user_list_path, "r") as file:
        reader = csv.DictReader(file)
        user_rows = []
        for row in reader:
            user_row = UserRow(**row)
            if user_row.is_incomplete():
                print(f"Skipping incomplete row {row}")
                continue
            user_rows.append(user_row)

        return user_rows
