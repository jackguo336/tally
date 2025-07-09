from peewee import SqliteDatabase
from pathlib import Path
import logging
import sqlite3

from tally.utils.date import get_file_timestamp


logger = logging.getLogger(__name__)


Path("data").mkdir(exist_ok=True)
db = SqliteDatabase("data/tally.db")
db.connect()


def backup_db():
    Path("backups").mkdir(exist_ok=True)
    
    backup_path = f"backups/tally_backup_{get_file_timestamp()}.db"
    logger.debug(f"Backing up database to {backup_path}")
    
    db_connection = db.connection()
    backup_connection = sqlite3.connect(backup_path)
    db_connection.backup(backup_connection)
    backup_connection.close()
