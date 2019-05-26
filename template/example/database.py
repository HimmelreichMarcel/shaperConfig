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
# Create the connection
cnx = create_engine(postgres_str)

#Read
pd.read_sql_query('''SELECT * FROM pokemon LIMIT 5;''', cnx)

poke_weights = pd.read_sql_query('''SELECT _pk as pokemon, weight_kg as weight FROM pokemon''', cnx)
poke_weights.head()

{
  "database": "db_name",
  "schema": "schema_name",
  "user": "user_name",
  "host": "host_url",
  "port": "port_num",
  "passw": "user_password"
}
import json

with open('config.json') as f:
    conf = json.load(f)


conn_str = "host={} dbname={} user={} password={}".format(host, database, user, passw)
conn = psycopg2.connect(conn_str)

import pandas as pd

df = pd.read_sql('select * from table_name', con=conn)

df = pd.DataFrame()
for chunk in pd.read_sql('select * from table_name', con=conn, chunksize=5000):
    df = df.append(chunk)


import psycopg2 as pg
import pandas.io.sql as psql
conn = pg.connect(database="abcd",user="postgres", password="xxxx")
df = pd.read_sql('SELECT * FROM "xyz"', conn)
df.head()



#MySQL
import os
import pymysql
import pandas as pd

host = os.getenv('MYSQL_HOST')
port = os.getenv('MYSQL_PORT')
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
database = os.getenv('MYSQL_DATABASE')

conn = pymysql.connect(
    host=host,
    port=int(port),
    user=user,
    passwd=password,
    db=database,
    charset='utf8mb4')

df = pd.read_sql_query(
    "SELECT DATE(created_at) AS date, COUNT(*) AS count FROM user GROUP BY date HAVING date >= '2017-04-01' ",
    conn)
df.tail(10)

#MariaDB
matplotlib inline
import MySQLdb as mariadb
import getpass  # so we don't need to store passwords on disk
import pandas as pd

# importing via mariadb directly into pandas dataframe:
password = getpass.getpass()  # asks for password in the console window so we don't store it here
conn = mariadb.connect('localhost','myusername',password,'dbname');
data = pd.io.sql.read_sql('select * from ipython_out', conn)
conn.close()
data.shape


#MongoDB
import os
import pandas as pd
import numpy as np
from IPython.core.display import display, HTML
import pymongo
from pymongo import MongoClient
print 'Mongo version', pymongo.__version__
client = MongoClient('localhost', 27017)
db = client.test
collection = db.people

#Import Data
collection.drop()
os.system('mongoimport -d test -c people dummyData.json')

#Check Access
cursor = collection.find().sort('Age',pymongo.ASCENDING).limit(3)
for doc in cursor:
    print doc


#Aggregation in MongoDB
pipeline = [
        {"$group": {"_id":"$Country",
             "AvgAge":{"$avg":"$Age"},
             "Count":{"$sum":1},
        }},
        {"$sort":{"Count":-1,"AvgAge":1}}
]
aggResult = collection.aggregate(pipeline) # returns a cursor
df1 = pd.DataFrame(list(aggResult)) # use list to turn the cursor to an array of documents
df1 = df1.set_index("_id")
df1.head()