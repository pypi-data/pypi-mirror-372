import numpy as np
import os
import pandas as pd
from gias3.learning import PCA
from sklearn.cross_decomposition import PLSRegression
import joblib


def pls_predict_PC(predictors, model, weights):
    '''
    using a sklearn random forest algorithm saved as a pkl file, predict the response from the given model
    '''
    model = joblib.load(model)
    prediction = (model.predict(predictors)).squeeze()
    # convert to sd not absolute weight
    init_pc_weights = np.zeros(len(prediction))
    for j in range(len(prediction)):
        init_pc_weights[j] = prediction[j] / np.sqrt(weights[j])
    return [init_pc_weights[0],0,0,0]

def rf_predict(predictors, model):
    '''
    using a sklearn random forest algorithm saved as a pkl file, predict the response from the given model
    '''
    model = joblib.load(model)
    prediction = (model.predict(predictors)).squeeze()
    return prediction
