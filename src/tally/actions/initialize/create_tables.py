import logging

from tally.services.db import db
from tally.models.db import ALL_MODELS


logger = logging.getLogger(__name__)


def create_tables():
    logger.debug("Creating tables if they do not exist: %s", ALL_MODELS)
    db.create_tables(ALL_MODELS, safe=True)
