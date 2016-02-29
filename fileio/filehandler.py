import os
import pickle


class FileHandler:
    def __init__(self):
        self.filedir = ''

    def setFiledir(self, filedir):
        self.filedir = filedir
        # return 'output/results/{},{}'.format(dataset.rhoNumber, dataset.phiNumber)

    def save(self, object, filename):
        directory = self.filedir

        if not os.path.exists(directory):
            os.makedirs(directory)

        filepath = '{}/{}.pkl'.format(directory, filename)

        with open(filepath, 'wb') as output:
            pickle.dump(object, output, pickle.HIGHEST_PROTOCOL)

    def load(self, filename):
        filepath = '{}/{}'.format(self.filedir, filename)

        f = file(filepath, 'rb')
        s = pickle.load(f)
        f.close()

        return s

    def findAll(self):
        files = []

        for file in os.listdir(self.filedir):
            if file.endswith('.pkl'):
                files.append(file)

        return sorted(files)
