import pandas as pd
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
