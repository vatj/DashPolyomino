import pandas as pd
import numpy as np
import re

def extract_parameters(file_string):
    parameters = dict()
    keys_short = ['ngenes', 'colours', 'threshold', 'builds']
    keys_long = ['ngenes', 'colours', 'threshold', 'builds', 'metric_colours', 'njiggle']
    test = re.findall(r'\d+', file_string)
    if(len(test) == 6):
        for key, value in zip(keys_long, test):
            parameters[key] = int(value)
        return parameters
    elif(len(test)== 4):
        for key, value in zip(keys_short, test):
            parameters[key] = int(value)
        return parameters
    else:
        raise ValueError('Too many or too few numbers in file')

def reshape_phenotypes(array):

    return array[0], array[1], str(tuple([array[0], array[1]])), array[2], array[3], array[4:].reshape(array[3], array[2]).astype(np.int8)


def import_phenotypes(file_str=str()):

    init = pd.read_csv(file_str, header=None, squeeze=False, converters={0 : lambda x: np.fromstring(x, dtype=np.int8, sep=' ')}).squeeze()
    data = pd.DataFrame()
    data['size'], data['subindex'], data['pIDs'], data['height'], data['width'], data['visual'] = list(zip(*init.apply(reshape_phenotypes)))

    return data
