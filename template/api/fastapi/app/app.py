from fastapi import FastAPI
from minio import Minio
import sklearn
from sklearn.externals import joblib
import numpy as np
import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

app = FastAPI()


@app.get("/")
async def test():
    return "This is a test message"


@app.get("/predict/{bucket}/{filename}/{predict_size}")
async def random_predict(bucket: str, filename: str, predict_size: int):
    try:
        minio_client = Minio(
            endpoint="minio:9000",
            access_key=os.environ["ACCESS_KEY"],
            secret_key=os.environ["SECRET_KEY"],
            secure=False)
        model = minio_client.get_object(bucket, filename).data.decode()
        loaded_model = joblib.load(model)
        data = np.random.randint(0, 2, size=(100, predict_size))
        return loaded_model.predict(data)
    except:
        return "Failed to predict"


@app.get('/notebook/run/{notebook}')
async def run_notebook(notebook: str):
    try:
        file_path = "/home/jovyan/work/"

        with open(file_path + notebook) as f:
            nb = nbformat.read(f, as_version=4)
        ep = ExecutePreprocessor(kernel_name='python3')
        ep.preprocess(nb, {'metadata': {'path': 'work/' + str(notebook)}})
        return "Run Notebook: " + str(notebook)
    except:
        return "Unable to run Notebook:" + str(notebook)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

    """
@app.get("/add_table/{database}")
async def add_row(database: str, user: str = None, password: str = None, db_name: str = None, row: dict = None):
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