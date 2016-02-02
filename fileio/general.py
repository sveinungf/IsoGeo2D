import glob
import os
import pickle


def save(object, filename):
    with open('output/results/{}.pkl'.format(filename), 'wb') as output:
        pickle.dump(object, output, pickle.HIGHEST_PROTOCOL)

def load(filename):
    #with open('output/results/{}'.format(filename), 'rb') as input:
    #    return pickle.load(input)
    f = file('output/results/{}'.format(filename), 'rb')
    s = pickle.load(f)
    f.close()

    return s

def findAll():
    files = []

    for file in os.listdir('output/results'):
        if file.endswith('.pkl'):
            files.append(file)

    return sorted(files)
