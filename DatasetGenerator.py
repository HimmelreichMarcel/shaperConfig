
import numpy as np
import pandas as pd

def generate(path, size_in_mb, feature_size):


    feature_list = []
    counter = 0
    while counter < feature_size:
        feature_list.append("feature" + str(counter))
        counter = counter + 1
    print(feature_list)



    frame1 = pd.DataFrame(np.random.randint(0,2, size=(100000, 1)), columns=["truth"])
    print(frame1)
    frame1.to_csv(path+"truth.csv")


    frame2 = pd.DataFrame(np.random.randint(0,2, size=(1000, feature_size)), columns= feature_list)
    print(frame2)
    frame2.to_csv(path+"prediction.csv")




generate("/home/standardheld/CONFIGS/", 1000, 5000)


