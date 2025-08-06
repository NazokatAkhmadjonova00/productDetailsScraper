# db.py

import psycopg2
from config import DB_CONFIG, PROJECT_SETTINGS
import logging

class DatabaseConnector:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            self.dry_run = PROJECT_SETTINGS.get("dry_run", False)

            if PROJECT_SETTINGS.get("debug", False):
                logging.info("Database connection successful.")
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            raise

    def execute(self, query, params=None, fetch=False):
        try:
            self.cursor.execute(query, params)
            if not self.dry_run:
                self.conn.commit()
            else:
                logging.info("Dry-Run: Query run successful, commit skipped.")

            if fetch:
                if self.cursor.description is not None:
                    return self.cursor.fetchone()
                else:
                    logging.warning("fetch=True set, but query returned no results.")
                    return None

        except psycopg2.ProgrammingError as e:
            self.conn.rollback()

            if "no results to fetch" in str(e).lower():
                logging.warning(f"No results to fetch for query:\n↳ {query[:100]}...\n↳ Params: {params}")
                return None
            else:
                logging.error(f"SQL ProgrammingError:\n{e}\n↳ Query: {query}\n↳ Params: {params}")
                raise

        except Exception as e:
            self.conn.rollback()
            logging.error(f"SQL-ERROR:\n{e}\n↳ Query: {query}\n↳ Params: {params}")
            raise


    def fetchall(self):
        try:
            if self.cursor.description is not None:
                return self.cursor.fetchall()
            else:
                logging.warning("fetchall() called but cursor.description is None (likely no SELECT executed).")
                return []
        except psycopg2.ProgrammingError as e:
            if "no results to fetch" in str(e).lower():
                logging.warning("fetchall() failed: no results to fetch (expected for non-SELECT).")
                return []
            else:
                logging.error(f"Unhandled ProgrammingError in fetchall(): {e}")
                self.conn.rollback()  # Wichtig: Verbindung retten
                raise
        except Exception as e:
            logging.error(f"Unexpected error during fetchall(): {e}")
            self.conn.rollback()
            raise


    def fetchone(self):
        try:
            if self.cursor.description is not None:
                return self.cursor.fetchone()
            else:
                logging.warning("fetchone() called but cursor.description is None (likely no SELECT executed).")
                return None
        except psycopg2.ProgrammingError as e:
            if "no results to fetch" in str(e):
                logging.warning("fetchone() failed: no results to fetch (expected for non-SELECT).")
                return None
            else:
                logging.error(f"Unhandled ProgrammingError in fetchone(): {e}")
                self.conn.rollback()  
                raise



    def close(self):
        self.cursor.close()
        self.conn.close()
        if PROJECT_SETTINGS.get("debug", False):
            logging.info("Database connection closed.")

    def rollback(self):
        self.conn.rollback()

    def commit(self):
        if not self.dry_run:
            self.conn.commit()

    def transaction(self):
        try:
            yield
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
