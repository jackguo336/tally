import tkinter
from tkinter import filedialog
from typing import List
from typing import TextIO
import csv

from tally.actions.score.team_score import TeamCumulativeScore
from tally.actions.score.score_config import ScoreConfig


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


def save_team_cumulative_score_to_csv(
    team_cumulative_scores: List[TeamCumulativeScore], config: ScoreConfig
):
    formatted_score_date_range = f"{config.score_start_date.strftime('%Y-%m-%d')}_to_{config.score_end_date.strftime('%Y-%m-%d')}"
    file = prompt_save_file(
        f"team_scores_{formatted_score_date_range}", ".csv", "team scores"
    )
    if not file:
        print("No file selected, skipping save")
        return

    with open(file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["Team", "Points"])
        for team_cumulative_score in team_cumulative_scores:
            writer.writerow(
                [team_cumulative_score.team.name, team_cumulative_score.points]
            )

    print(f"Successfully saved team scores to {file}")
