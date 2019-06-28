from flask import Flask, request
from minio import Minio
import sklearn
from sklearn.externals import joblib
import numpy as np
import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

app = Flask(__name__)


@app.route("/")
def test():
    return "This is a test message"


@app.route('/predict/<bucket>/<filename>/<predict_size>')
def random_predict(bucket, filename, predict_size):
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


@app.route('/notebook/run/<notebook>')
def run_notebook(notebook):
    try:
        file_path = "/home/jovyan/work/"

        with open(file_path + notebook) as f:
            nb = nbformat.read(f, as_version=4)
        ep = ExecutePreprocessor(kernel_name='python3')
        ep.preprocess(nb, {'metadata': {'path': 'work/'+str(notebook)}})
        return "Run Notebook: " + str(notebook)
    except:
        return "Unable to run Notebook:" + str(notebook)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')