from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/add_table/{database}")
def add_row(database: str, user: str = None, password: str = None, db_name: str = None, row: dict = None):
    if database == "postgres":
        import psycopg2
        import sqlalchemy
        from sqlalchemy import create_engine

        POSTGRES_ADDRESS = 'db.panoply.io'  ## INSERT YOUR DB ADDRESS IF IT'S NOT ON PANOPLY
        POSTGRES_PORT = '5432'
        POSTGRES_USERNAME = user
        POSTGRES_PASSWORD = password  ## CHANGE THIS TO YOUR PANOPLY/
        POSTGRES_DBNAME = db_name  ## CHANGE THIS TO YOUR DATABASE NAME

        postgres_str = (
            'postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'.format(username=POSTGRES_USERNAME,
                                                                                    password=POSTGRES_PASSWORD,
                                                                                    ipaddress=POSTGRES_ADDRESS,
                                                                                    port=POSTGRES_PORT,
                                                                                    dbname=POSTGRES_DBNAME))
    elif database == "mysql" or database == "maria":
        import os
        import pymysql

        host = os.getenv('MYSQL_HOST')
        port = "3306"
        user = user
        password = password
        database = db_name

        conn = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            passwd=password,
            db=database,
            charset='utf8mb4')

    elif database == "mongo":
        import os
        import pymongo
        from pymongo import MongoClient
        client = MongoClient('localhost', 27017)
        db = client.test
        collection = db.people


"""

# Postgres
import pandas as pd
import psycopg2
import sqlalchemy
import matplotlib as plt
from sqlalchemy import create_engine
# Postgres username, password, and database name
POSTGRES_ADDRESS = 'db.panoply.io' ## INSERT YOUR DB ADDRESS IF IT'S NOT ON PANOPLY
POSTGRES_PORT = '5439'
POSTGRES_USERNAME = 'username' ## CHANGE THIS TO YOUR PANOPLY/POSTGRES USERNAME
POSTGRES_PASSWORD = '*****' ## CHANGE THIS TO YOUR PANOPLY/
POSTGRES_DBNAME = 'database' ## CHANGE THIS TO YOUR DATABASE NAME
# A long string that contains the necessary Postgres login information
postgres_str = ('postgresql://{username}:{password}@{ipaddress}:{port}/{dbname}'.format(username=POSTGRES_USERNAME,
                                                                                        password=POSTGRES_PASSWORD,
                                                                                        ipaddress=POSTGRES_ADDRESS,
                                                                                        port=POSTGRES_PORT,
                                                                                        dbname=POSTGRES_DBNAME))

"""