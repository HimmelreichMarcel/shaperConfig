from flask import Flask, request
from minio import Minio
import sklearn
from sklearn.externals import joblib
import numpy as np
import os
app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')