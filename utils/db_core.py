import sqlite3
from typing import Union


class DbCore:
    def __init__(self) -> None:
        from data.config import DB_NAME
        self._path_to_db = DB_NAME

    @property
    def connection(self) -> sqlite3:
        return sqlite3.connect(self._path_to_db)

    def execute(self, sql_query: str = "", parameters: Union[list, tuple] = (),
                fetchone: bool = False, fetchall: bool = False, commit: bool = False) -> list:

        if isinstance(parameters, list):
            parameters = tuple(parameters)

        connection = self.connection

        query_output = connection.cursor().execute(sql_query, parameters)


        if fetchone:
            return query_output.fetchone()
        elif fetchall:
            return query_output.fetchall()

        if commit:
            connection.commit()

        connection.close()


    def create_table(self) -> None:
        queries = [
        """
        CREATE TABLE `ideas`(
            user_id   VARCHAR(255) NOT NULL,
            username  VARCHAR(32)  NOT NULL,
            firstname VARCHAR(255) NOT NULL,
            text      TEXT         NOT NULL,
            date      VARCHAR(128) NOT NULL
        )
        """,
        """
        CREATE TABLE `count`(
            user_id  VARCHAR(255) NOT NULL,
            count    INTEGER NOT NULL,
            timeleft INTEGER NOT NULL
        )
        """
        ]
        for query in queries: self.execute(query, commit=True)

    def get_ideas(self) -> Union[list, tuple]:
        return self.execute("SELECT * FROM `ideas`", fetchall=True)

    def clear(self) -> None:
        self.execute("DELETE FROM `ideas`", commit=True)

    def insert_user(self, data) -> None:
        query = """
            INSERT INTO `ideas` (user_id, username, firstname, text, date)
            VALUES (?,?,?,?,?)
        """
    
        self.execute(query, data, commit=True)

    def add_user_to_count(self, user_id) -> None:
        self.connection.execute("INSERT INTO `count` (user_id, count, timeleft) VALUES (?,?,?)",(user_id, 1, 0), commit=True)

    def get_user_count(self, user_id) -> Union[list, tuple]:
        return self.connection.execute(f"SELECT * FROM `count` WHERE user_id={user_id}", fetchone=True)

    def restrict_for_time(self, data) -> None:
        self.connection.execute(f"UPDATE `count` SET count=5, timeleft={data[0]} WHERE user_id={data[1]}", commit=True)

    def increment_user_count(self, data) -> None:
        self.connection.execute(f"UPDATE `count` SET count={data[1]} WHERE user_id={data[0]}", commit=True)

