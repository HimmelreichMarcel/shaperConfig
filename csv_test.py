import pandas as pd
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn import metrics
data = pd.read_csv("/home/standardheld/CONFIGS/small_dataset.csv")
print(data.shape)

classifier = svm.SVC(gamma=0.001, C=100., verbose=True)
Y = data.iloc[:50000, -1]
X = data.iloc[:50000, :-1]
Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, test_size=0.3, random_state=4)

classifier.fit(Xtrain, Ytrain)
Ypred = classifier.predict(Xtest)

# Get Metrics
metric = metrics.accuracy_score(Ytest, Ypred)
print(metrics)