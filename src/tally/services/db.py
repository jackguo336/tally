from peewee import SqliteDatabase
from pathlib import Path
import datetime
import logging
import sqlite3


logger = logging.getLogger(__name__)


Path("data").mkdir(exist_ok=True)
db = SqliteDatabase("data/tally.db")
db.connect()


def backup_db():
    current_time = datetime.datetime.now().isoformat()
    Path("backups").mkdir(exist_ok=True)
    
    backup_path = f"backups/tally_backup_{current_time}.db"
    logger.debug(f"Backing up database to {backup_path}")
    
    db_connection = db.connection()
    backup_connection = sqlite3.connect(backup_path)
    db_connection.backup(backup_connection)
    backup_connection.close()
