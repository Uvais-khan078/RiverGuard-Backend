from database_config import engine
from sqlalchemy import text

def create_schema():
    with engine.connect() as connection:
        with connection.begin():
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS myuser_schema;"))
        print("Schema 'myuser_schema' created or already exists.")

if __name__ == "__main__":
    create_schema()
