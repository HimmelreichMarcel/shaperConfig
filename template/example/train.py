#Scitkit
from sklearn import svm
from sklearn.model_selection import train_test_split
import os
from sklearn import metrics
from sklearn.externals import joblib

#Minio
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
# Postgres
import pandas as pd
import psycopg2
import sqlalchemy
from sqlalchemy import create_engine

# Postgres username, password, and database name
DIALECT = os.environ["DB_DIALECT"]
DB_ADDRESS = os.environ["DB_ADRESS"]
DB_PORT = os.environ["DB_PORT"]
DB_USERNAME = os.environ["USER"]
DB_PASSWORD = os.environ["PWD"]
DB_NAME = os.environ["DATABASE"]
# A long string that contains the necessary Postgres login information
db_str = ('{dialect}://{username}:{password}@{ipaddress}/{dbname}'.format(dialect=DIALECT,
                                                                                username=DB_USERNAME,
                                                                                password=DB_PASSWORD,
                                                                                ipaddress=DB_ADDRESS,
                                                                                dbname=DB_NAME))
# Create the connection
cnx = create_engine(db_str)

#Read
data_frame = pd.read_sql_query('''SELECT * FROM ''' + os.environ["TABLE"], cnx)


#Train Model


classifier = svm.SVC(gamma=0.001, C=100.)

Y = data_frame.iloc[:, -1]
X = data_frame.iloc[:, :-1]
Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, test_size=0.3, random_state=4)

classifier.fit(Xtrain, Ytrain)

Ypred = classifier.predict(Xtest)

#Get Metrics
metrics = metrics.accuracy_score(Ytest, Ypred)

#Dump Model

# create a connection to the object store
minio_client = Minio(
    endpoint="minio:9000",
    access_key=os.environ["ACCESS_KEY"],
    secret_key=os.environ["SECRET_KEY"],
    secure=False)


# create a minio bucket
try:
    minio_client.make_bucket("test-bucket")
except BucketAlreadyOwnedByYou as err:
       pass
except BucketAlreadyExists as err:
       pass
except ResponseError as err:
       raise

filename = 'model.sav'
joblib.dump(classifier, filename)

# write the object to minio
minio_client.put_object(
    bucket_name="test-bucket",
    object_name="sample-file.txt",
    file_path="./"+filename)

