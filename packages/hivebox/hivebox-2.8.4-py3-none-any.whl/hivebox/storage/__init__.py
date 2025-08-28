import sqlite3
from pathlib import Path
from typing import List


class SQLite:
    def __init__(self, create_sql, db_name):
        self.db_name = db_name

        if not Path(self.db_name).exists():
            with sqlite3.connect(self.db_name) as conn:
                conn.execute(create_sql)

    def get_data(self, table_name, order_by=None):
        with sqlite3.connect(self.db_name) as conn:
            query = f"SELECT * FROM {table_name}"
            if order_by:
                ascending = True
                if order_by.startswith("-"):
                    order_by = order_by[1:]
                    ascending = False
                query += f" ORDER BY {order_by} {'ASC' if ascending else 'DESC'}"
            print(query)
            result = conn.execute(query)
            colnames = [d[0] for d in result.description]
            return [dict(zip(colnames, result_list)) for result_list in result.fetchall()]

    def add_data(self, table_name, input_data: List[dict]):
        if len(input_data) == 0:
            return
        cols = input_data[0].keys()
        data = [tuple([item[col] for col in cols]) for item in input_data]
        with sqlite3.connect(self.db_name) as conn:
            sql = f"INSERT INTO {table_name} ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})"
            return conn.executemany(sql, data)

if __name__ == "__main__":
    db = SQLite("""
    CREATE TABLE people (
                        firstname varchar,
                        surname varchar,
                        age numeric,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                    );
    """)
    db.add_data('people', [
        {'firstname': 'Jakub', 'surname': 'Kowalski', 'age': 33},
        {'firstname': 'Łukasz', 'surname': 'Piłatowski', 'age': 28},
    ])

    print(db.get_data('people'))