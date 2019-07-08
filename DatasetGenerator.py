
import numpy as np
import pandas as pd

def generate(path, size_in_mb, feature_size):


    feature_list = []
    counter = 0
    while counter < feature_size:
        feature_list.append("feature" + str(counter))
        counter = counter + 1
    print(feature_list)




    frame2 = pd.DataFrame(np.random.randint(0,2, size=(size_in_mb, feature_size)), columns= feature_list)

    frame2.to_csv(path+"dataml.csv", index=False)


    print(frame2)

generate("/home/standardheld/CONFIGS/", 1000000, 50)


