import pandas as pd


frame = pd.read_csv("/home/marcel/data/small_dataset.csv").drop(['Unnamed: 0'],axis=1)
frame.to_csv("/home/standardheld/small_dataset.csv", index=False)
print(frame)