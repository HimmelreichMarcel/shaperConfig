from flask import Flask, request
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
import sklearn
from sklearn import metrics
from sklearn import svm
from sklearn.model_selection import train_test_split
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
import joblib
import numpy as np
import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert.preprocessors import CellExecutionError
import d6tstack
from pymongo import MongoClient
import pymysql

app = Flask(__name__)


@app.route("/")
def test():
    return "This is a test message"

@app.route('/test')
def hello_world():
    return "Test Page"

@app.route('/predict/<bucket>/<filename>/<predict_size>')
def random_predict(bucket, filename, predict_size):
    try:
        minio_client = Minio(
            endpoint="minio:9000",
            access_key="test",
            secret_key="testtest",
            secure=False)
        model = minio_client.get_object(bucket, filename)
        with open(filename, 'wb') as file_data:
            for d in model.stream(32 * 1024):
                file_data.write(d)
        loaded_model = None
        with open(filename, 'rb') as file:
            loaded_model = joblib.load(file)
        data = np.random.randint(0, 2, size=(100, int(predict_size)))
        predict = loaded_model.predict(data)
        return "Predict success" + "\n" + str(loaded_model) + "\n" + str(predict)
    except Exception as error:
        msg = []
        msg.append("Failed to Predict \n")
        if hasattr(error, 'message'):
            msg.append(error.message)
        else:
            msg.append(error)
        return str(msg)


@app.route('/db/write/<filename>/<db>/<db_name>/<table>')
def write_db_data(filename, db, db_name, table):
    try:
        dataframe = pd.read_csv("/data/" + filename)
        db_str = get_db_str(db, db_name)
        write_data_to_database(db,db_str, table, dataframe)
        return str(dataframe.head(10))
    except Exception as error:
        return "Error Writing Data to Database" + str(error)


@app.route('/learn/train/<db>/<db_name>/<table>')
def train_model(db, db_name, table):
    try:
        db_str = get_db_str(db,db_name)
        data = read_db_data(db, db_str, table)

        classifier = svm.SVC(gamma=0.001, C=100.)

        Y = data.iloc[:1000, -1]
        X = data.iloc[:1000, :-1]
        Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, test_size=0.3, random_state=4)

        classifier.fit(Xtrain, Ytrain)
        Ypred = classifier.predict(Xtest)

        #Get Metrics
        metric = metrics.accuracy_score(Ytest, Ypred)

        store_data(classifier, "model.joblib")

        return "Training Done" + str(metric) + str(data)
    except Exception as error:
        return "!!!Failed Train Model!!!" + str(error)

def store_data(classifier, filename):
    minio_client = Minio(
        endpoint="minio:9000",
        access_key="test",
        secret_key="testtest",
        secure=False)
    try:
        minio_client.make_bucket("test-bucket")
    except BucketAlreadyOwnedByYou as err:
        pass
    except BucketAlreadyExists as err:
        pass
    except ResponseError as err:
        raise

    joblib.dump(classifier, filename)

    with open(filename, 'rb') as file_data:
        file_stat = os.stat(filename)
        minio_client.put_object("test-bucket", filename, file_data, file_stat.st_size)

def get_db_str(database, db_name):
    if database == "postgres":
        DIALECT = "postgresql+psycopg2"
        DB_ADDRESS = "database"
        DB_PORT = "5432"
        DB_USERNAME = "admin"
        DB_PASSWORD = "admin"
        DB_NAME = db_name
    elif database == "mysql" or database == "mariadb":
        DIALECT = "mysql+pymysql"
        DB_ADDRESS = "database"
        DB_PORT = "3306"
        DB_USERNAME = "root"
        DB_PASSWORD = "admin"
        DB_NAME = db_name
    elif database == "mongo":
        DIALECT = "mongodb"
        DB_ADDRESS = "database"
        DB_PORT = "27017"
        DB_USERNAME = "admin"
        DB_PASSWORD = "admin"
        DB_NAME = "admin"
    db_str = ('{dialect}://{username}:{password}@{ipaddress}/{dbname}'.format(dialect=DIALECT,
                                                                              username=DB_USERNAME,
                                                                              password=DB_PASSWORD,
                                                                              ipaddress=DB_ADDRESS,
                                                                              dbname=DB_NAME))
    return db_str

def read_db_data(database, db_str, table):
    try:
        if database == "postgres":
            cnx = create_engine(db_str)
            data = pd.read_sql_query('''SELECT * FROM ''' + str(table), cnx)
        elif database == "mysql" or database == "mariadb":
            cnx = create_engine(db_str)
            data = pd.read_sql_query('''SELECT * FROM ''' + str(table), cnx)
        elif database == "mongo":
            client = MongoClient(db_str)
            db = client.test
            db = db.train_table
            data = pd.DataFrame(list(db.find()))
        return data
    except Exception as error:
        return "!!!Failed read Data!!!" + str(error)

def write_data_to_database(database, db_str, table, data):
    try:
        if database == "postgres":
            d6tstack.utils.pd_to_psql(data, db_str, 'train_table', if_exists='replace')
        elif database == "mysql" or database == "mariadb":
            d6tstack.utils.pd_to_psql(data, db_str, 'train_table', if_exists='replace')
        elif database == "mongo":
            client = MongoClient(db_str)
            db = client.test
            db = db.train_table
            db.insert_many(data.to_dict('records'))
    except Exception as error:
        return "!!!Failed Write Data!!!" + str(error)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')