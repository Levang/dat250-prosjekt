import sqlalchemy as s
from typing import Dict


class SqlDb:
    def __init__(self, dbPath="../database.db"):
        self.engine: s.engine.create_engine = s.create_engine(f"sqlite:///{dbPath}", echo=True)
        self.conn: s.engine.Connection = self.engine.connect()
        self.tables: Dict[str, s.Table] = {}

    def create_users_table(self):
        meta = s.MetaData()
        users = s.Table(
            "users", meta,
            s.Column("email", s.String, primary_key=True),
            s.Column("password", s.String),
        )
        self.tables["users"] = users
        users.insert()
        meta.create_all(self.engine)

    def add_user(self, emailVal, passVal):
        table = self.tables["users"]
        ins = table.insert().values(email=emailVal, password=passVal)
        self.conn.execute(ins)


if __name__ == '__main__':
    db = SqlDb()
    db.create_users_table()
    print("-"*10)
    db.add_user("abcd", "123")
    print("-"*10)
