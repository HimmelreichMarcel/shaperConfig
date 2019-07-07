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


def get_minio_data(bucket, filename):
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

        with open(filename, 'rb') as file:
            return str(file)
    except Exception as error:
        return error



def write_minio_data(bucket, path, filename):
    try:
        minio_client = Minio(
            endpoint="minio:9000",
            access_key="test",
            secret_key="testtest",
            secure=False)

        with open(path, 'rb') as file_data:
            file_stat = os.stat(path)
            minio_client.put_object("test-bucket", filename, file_data, file_stat.st_size)
            return str(file_data)
    except Exception as error:
        return error

@app.route('/db/write/<filename>/<db>/<db_name>/<table>')
def write_db_data(filename, db, db_name, table):
    try:
        if db == "minio":
            dataframe = write_minio_data("test-bucket", "/data/" + str(filename), filename)
        else:
            dataframe = pd.read_csv("/data/" + filename)
            db_str = get_db_str(db, db_name)
            write_data_to_database(db,db_str, table, dataframe)
        return str(dataframe)
    except Exception as error:
        return "Error Writing Data to Database" + str(error)


@app.route('/db/table/<db>/<db_name>/<table>/<count>')
def create_table(db, db_name, table, count):
    try:
        cnx = create_engine(get_db_str(db, db_name))
        con = cnx.connect()
        sql_command = "CREATE TABLE " + str(db_name) + "." + str(table) + " ("
        counter = 0
        while counter < int(count):
            if counter == int(count) - 1:
                sql_command += "feature" + str(counter) + " INTEGER"
            else:
                sql_command += "feature" + str(counter) + " INTEGER,"
            counter = counter + 1
        sql_command += ")"
        msg = con.execute(sql_command)
        return str(msg)
    except Exception as error:
        return "Failed to Create Table" + str(error)




@app.route('/db/permission/<db>/<db_name>')
def permission(db, db_name):
    try:
        cnx = create_engine(get_db_str(db, db_name))
        con = cnx.connect()
        sql_command = []
        sql_command.append("GRANT ALL PRIVILEGES ON *.* TO \'admin\'@\'%\' IDENTIFIED BY \'admin\' WITH GRANT OPTION; "
                   "GRANT ALL PRIVILEGES ON *.* TO \'admin'@'database\' IDENTIFIED BY \'admin\' WITH GRANT OPTION; "
                   "FLUSH PRIVILEGES;")
        sql_command.append("GRANT ALL PRIVILEGES ON *.* TO \'root\'@\'%\' IDENTIFIED BY \'admin\' WITH GRANT OPTION; "
                   "GRANT ALL PRIVILEGES ON *.* TO \'root'@'database\' IDENTIFIED BY \'admin\' WITH GRANT OPTION; "
                   "FLUSH PRIVILEGES;")
        msg = con.execute(sql_command)
        return str(msg)
    except Exception as error:
        return "Failed to Create Table" + str(error)

@app.route('/learn/status/<bucket>/<filename>')
def status(bucket, filename):
    found = False
    try:
        minio_client = Minio(
            endpoint="minio:9000",
            access_key="test",
            secret_key="testtest",
            secure=False)
        model = minio_client.stat_object(bucket, filename)
        found = True
    except Exception as error:
        #data = read_db_data(db, db_str, table)
        return "!!!Failed to check Data in Minio!!!" + str(error)# +
    if found:
        return "true"
    else:
        return "false"



@app.route('/learn/train/<db>/<db_name>/<table>')
def train_model(db, db_name, table):
    try:
        db_str = get_db_str(db,db_name)
        if db == "minio" or db == "None":
            data = pd.read_csv("/data/small_dataset.csv")
        else:
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
        #data = read_db_data(db, db_str, table)
        return "!!!Failed Train Model!!!" + str(error)# + str(data)

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
        DB_USERNAME = "admin"
        DB_PASSWORD = "admin"
        DB_NAME = db_name
    elif database == "mongo":
        DIALECT = "mongodb"
        DB_ADDRESS = "database"
        DB_PORT = "27017"
        DB_USERNAME = "admin"
        DB_PASSWORD = "admin"
        DB_NAME = db_name
    else:
        DIALECT = "mongodb"
        DB_ADDRESS = "database"
        DB_PORT = "27017"
        DB_USERNAME = "admin"
        DB_PASSWORD = "admin"
        DB_NAME = db_name
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