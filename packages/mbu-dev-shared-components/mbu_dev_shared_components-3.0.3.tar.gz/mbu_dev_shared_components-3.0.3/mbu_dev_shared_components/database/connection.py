"""Handles the RPA connection"""

from .constants import Constants
from .utility import Utility
from .logging import Log


class RPAConnection(
    Constants,
    Utility,
    Log,
):
    """Class for running database related """
    def __init__(self, db_env: str = "PROD", commit: bool | str = False):
        Constants.__init__(self)
        Utility.__init__(self)
        Log.__init__(self)
        self.db_env = db_env
        self.commit = commit if isinstance(commit, bool) else commit == "True"
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = self.connect_to_db(autocommit=False, db_env=self.db_env)
        self.cursor = self.conn.cursor()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.commit:
            print("Commiting transaction...")
            self.conn.commit()
        else:
            print("Rolling back transaction....")
            self.conn.rollback()
        print("Closing conection...")
        self.close()
        print("Connection closed.")

    def rollback(self):
        """Rollback transaction on connection if autocommit is not enabled"""
        if self.autocommit:
            raise RuntimeError("Cannot rollback: autocommit is enabled.")
        self.conn.rollback()

    def close(self):
        """Closes connection"""
        self.cursor.close()
        self.conn.close()
