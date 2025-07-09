import datetime


class ScoreConfig:
    def __init__(
        self,
        score_start_date: datetime.date,
        score_end_date: datetime.date,
        time_zone: str,
    ):
        self.score_start_date = score_start_date
        self.score_end_date = score_end_date
        self.time_zone = time_zone
