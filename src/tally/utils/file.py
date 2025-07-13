import tkinter
from tkinter import filedialog
from typing import List, TextIO, Tuple


class FileType:
    csv = ("CSV files", "*.csv")


def prompt_save_file(
    initial_file_name: str, default_extension: str, file_description: str
) -> TextIO | None:
    print(f"Use the pop-up file explorer to select the file to save {file_description}")

    root = tkinter.Tk()
    # Prevents the tkinter window from appearing
    root.withdraw()

    file = filedialog.asksaveasfilename(
        title=f"Save {file_description}",
        initialfile=initial_file_name,
        defaultextension=default_extension,
    )

    root.destroy()

    return file


def prompt_select_file(
    file_description: str, file_types: List[Tuple[str, str]]
) -> str | None:
    root = tkinter.Tk()
    # Prevents the tkinter window from appearing
    root.withdraw()

    path = filedialog.askopenfilename(
        title=f"Select the {file_description}",
        filetypes=file_types,
    )

    root.destroy()

    if path:
        print(f"Selected file: {path}")

    return path
