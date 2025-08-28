"""This module handles logging in the RPA database"""

from datetime import datetime
import time
import socket


class Log:
    """Base class for handling logging"""
    def log_event(
            self,
            log_db: str,
            level: str,
            message: str,
            context: str,
    ):
        """Logs the inputted parameters in """
        created_at = datetime.now()
        query = f"""
            INSERT INTO RPA.{log_db}
                ([level]
                ,[message]
                ,[created_at]
                ,[context])
            VALUES
                (?
                ,?
                ,?
                ,?)
            """

        params = [level, message, created_at, context]
        self.execute_query(query=query, params=params)

    def _get_log_event(
            self,
            log_db: str,
            level: str,
            message: str,
            context: str,
    ):
        query = f"""
            SELECT
                ([level]
                ,[message]
                ,[created_at]
                ,[context])
            FROM
                RPA.{log_db}
            WHERE
                level={level},
                message={message},
                context={context}
            """

        res = self.execute_query(query=query)
        return res

    def get_latest_log(
            self,
            log_db: str,
    ):
        """Retrieve latest log message from database"""
        query = f"""
            SELECT TOP (1)
                [level]
                ,[message]
                ,[created_at]
                ,[context]
            FROM
                RPA.{log_db}
            ORDER BY
                created_at desc
            """

        res = self.execute_query(query=query)
        return res

    def _send_heartbeat(
            self,
            servicename,
            status,
            details
    ):
        """Function to send heartbeat to database"""
        hostname = socket.gethostname()
        params = {
            "ServiceName": (str, servicename),
            "Status": (str, status),
            "HostName": (str, hostname),
            "Details": (str, details)
        }
        result = self.execute_stored_procedure(
            stored_procedure='rpa.sp_UpdateHeartbeat',
            params=params)
        if result["success"] is not True:
            print(result["error_message"])

    def log_heartbeat(
            self,
            stop: str | bool,
            servicename: str,
            heartbeat_interval: int,
            details: str = "",
    ):
        """Function to log heartbeat"""
        # Update connection such that it autocommits
        self.conn.autocommit = True  # Sets class attribute
        if isinstance(stop, str):
            stop = stop == "True"
        if not isinstance(heartbeat_interval, int):
            heartbeat_interval = int(heartbeat_interval)
        while not stop:
            status = "RUNNING"
            self._send_heartbeat(
                servicename,
                status,
                details,
            )
            time.sleep(heartbeat_interval)
        status = "STOPPED"
        self._send_heartbeat(
            servicename,
            status,
            details,
        )

    def get_heartbeat(self, service_name: str):
        """Get hearbeats """
        query = f"""
            SELECT
                *
            FROM
                [RPA].[rpa].[ServiceHeartbeat]
            WHERE
                ServiceName = '{service_name}'
        """
        res = self.execute_query(query)
        return res
