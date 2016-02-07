import glob
import os
import pickle


def __filedir(dataset):
    return 'output/results/{},{}'.format(dataset.rhoNumber, dataset.phiNumber)

def save(dataset, object, filename):
    directory = __filedir(dataset)

    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = '{}/{}.pkl'.format(directory, filename)

    with open(filepath, 'wb') as output:
        pickle.dump(object, output, pickle.HIGHEST_PROTOCOL)

def load(dataset, filename):
    filepath = '{}/{}'.format(__filedir(dataset), filename)

    f = file(filepath, 'rb')
    s = pickle.load(f)
    f.close()

    return s

def findAll(dataset):
    files = []

    for file in os.listdir(__filedir(dataset)):
        if file.endswith('.pkl'):
            files.append(file)

    return sorted(files)
