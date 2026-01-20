from typing import List
from pydantic import BaseModel
import csv
import logging
import traceback

logger = logging.getLogger(__name__)


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
    skipped_row_count = 0

    with open(user_list_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        user_rows = []
        for idx, row in enumerate(reader):
            try:
                user_row = UserRow(**row)
            except Exception:
                print(f"Failed to read entry at row {idx + 1}")
                logger.debug(
                    f"Failed to read entry {row} at row {idx + 1}:\n{traceback.format_exc()}"
                )
                skipped_row_count += 1
                continue

            if user_row.is_incomplete():
                print(f"Skipping incomplete entry at row {idx + 1}")
                logger.debug(f"Skipped incomplete entry {row} at position {idx + 1}")
                skipped_row_count += 1
                continue

            user_rows.append(user_row)

        print(
            f"Parsed {len(user_rows)} user rows. Skipped {skipped_row_count} incomplete or "
            "incorrectly formatted rows (see logs for details)."
        )
        return user_rows
