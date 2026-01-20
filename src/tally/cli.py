import questionary
import logging
import sys
from pathlib import Path
import traceback

from tally.actions.initialize.initialize import initialize
from tally.actions.reset.reset import reset
from tally.actions.track.track import track
from tally.actions.score.score import score
from tally.actions.export.export import export
from tally.actions.load.load import load
from tally.utils.date import get_file_timestamp


def configure_logging():
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(logging.ERROR)

    Path("logs").mkdir(exist_ok=True)
    file_handler = logging.FileHandler(f"logs/tally_{get_file_timestamp()}.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    logging.basicConfig(level=logging.DEBUG, handlers=[stdout_handler, file_handler])


actions = {
    "initialize": "Configure challenge",
    "track": "Track activities",
    "score": "Calculate scores",
    "reset": "Delete all data",
    "export": "Export activity data",
    "load": "Import activity data",
    "exit": "Exit",
}


def prompt_action() -> str:
    return (
        questionary.select(
            "Select an operation",
            choices=list(actions.values()),
        ).ask()
        or actions["exit"]
    )


def prompt_exit_after_failure(action: str) -> bool:
    return questionary.confirm(
        "Failed to complete action. See logs for details. Exit the application now?",
        default=False,
    ).ask()


def app():
    configure_logging()
    logger = logging.getLogger(__name__)

    should_exit = False
    while not should_exit:
        action = prompt_action()
        try:
            if action == actions["initialize"]:
                initialize()
            elif action == actions["track"]:
                track()
            elif action == actions["score"]:
                score()
            elif action == actions["reset"]:
                reset()
            elif action == actions["export"]:
                export()
            elif action == actions["load"]:
                load()
            elif action == actions["exit"] or not action:
                should_exit = True
        except Exception:
            logger.debug(
                f"Failed to complete action {action}:\n{traceback.format_exc()}"
            )
            should_exit = prompt_exit_after_failure(action)


if __name__ == "__main__":
    app()
