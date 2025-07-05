from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

PASSWORD = os.getenv("Password")

def create_my_db():
    host = "localhost"
    port = "5432"
    user = "postgres"
    password = "PASSWORD"
    db_name = "my_db"

    system_db_url = f"postgresql://{user}:{password}@{host}:{port}/postgres"
    engine = create_engine(system_db_url)
    with engine.connect() as conn:
        conn.execute_option(isolation_level = "AUTOCOMMIT")
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :dbname")), {"dbname":db_name}
        if not result.fetchone():
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"Database {db_name} Created")
        else:
            print("Database already created")
    database_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    engine_my = create_engine(database_url)
    my_script = '''
        CREATE TABLE IF NOT EXIST users(
        id INT PRIMARY KEY,
        Name VARCHAR(100),
        Mail VARCHAR(100)
        );
        INSERT INTO users (Name, Mail) VALUES
        ("Example", "email_1")

        '''
    with engine_my.connect():
        try:
            for statement in my_script.split(";"):
                statement = statement.split()
                if statement:
                    conn.execute(text(statement))
                conn.commit()
                print("Successfully")
        except:
            print("Error for script running")
            conn.rollback()
    return engine_my

engine_my = create_my_db()
db = SQLDatabase(engine_my)

