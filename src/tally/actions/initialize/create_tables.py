import logging

from tally.services.db import db
from tally.models.user import User
from tally.models.team import Team
from tally.models.config import Config
from tally.models.activity import Activity


logger = logging.getLogger(__name__)


def create_tables():
    all_models = [User, Team, Config, Activity]
    logger.debug("Creating tables if they do not exist: %s", all_models)
    db.create_tables(all_models, safe=True)
