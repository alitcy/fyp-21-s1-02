from sklearn.svm import OneClassSVM
from sklearn.model_selection import train_test_split
import pathlib
import pandas
import numpy as np
import pickle
import os
import csv
np.set_printoptions(suppress=True)

# path = pathlib.Path().absolute()
path = "typing-habits"

# Equal error rate
def evaluateEER(user_scores, imposter_scores):
    labels = [0]*len(user_scores) + [1]*len(imposter_scores)
    fpr, tpr, thresholds = roc_curve(labels, user_scores + imposter_scores)
    missrates = 1 - tpr
    farates = fpr
    dists = missrates - farates
    idx1 = np.argmin(dists[dists >= 0])
    idx2 = np.argmax(dists[dists < 0])
    x = [missrates[idx1], farates[idx1]]
    y = [missrates[idx2], farates[idx2]]
    a = ( x[0] - x[1] ) / ( y[1] - x[1] - y[0] + x[0] )
    eer = x[0] + a * ( y[0] - x[0] )
    return eer

def getData(username):
    user_path = str(path) + "/" + username + "/" + username + ".csv"
    return pandas.read_csv(user_path, header=None)

# Create model
# Call this method to make individual models.
# Parameter: csv file that contains 10 rows of data
def create_model(user):
    # Get data
    user_data = user.iloc[:, 5:]
    user_name = user.iloc[0,0]

    # Train and test data split
    train, test = train_test_split(user_data, test_size=.1)

    # For 10 samples
    clf = OneClassSVM(kernel='rbf', nu=0.027, gamma=0.35)

    clf.fit(train)

    # Saving the model
    filename = str(user_name) + '_model.sav'
    user_path = path + "/" + user_name + "/" + filename
    pickle.dump(clf, open(user_path, 'wb'))

# Predict if user will be authenticated
# Call this function to authenticate user when logging in
# Parameter: csv file that contains 1 row, which is the log in attempt data
def predict(test_user):
    test_user_data = test_user.iloc[0, 5:]
    test_user_name = test_user.iloc[0, 0]

    # Retrieve saved model
    model_path = path + "/" + str(test_user_name) + '/' + str(test_user_name) +'_model.sav'
    user_model = pickle.load(open(model_path, 'rb'))

    #newpred_test = gclf.predict(newtest)
    new_test_user_data = test_user_data.values.reshape(1,-1)
    pred = user_model.predict(new_test_user_data)
    return pred[0]

# This function is used for login verification of typing habit
# because we have a temporary data to verify with the model
def convertNPArrayToDF(npArray):
    col_array = [] # to get the number of columns needed in the dataframe
    for x in range(len(npArray)):
        col_array.append(str(x))

    npArray.shape = (1, len(col_array))
    df = pandas.DataFrame(data=npArray, index=["1"], columns=col_array) # index=1 because its just one row
    return df