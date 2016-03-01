import sys

import summary
from fileio.filehandler import FileHandler
from dataset import Dataset
from modeltype import ModelType


datasetRho = int(sys.argv[1])
datasetPhi = int(sys.argv[2])

interestingTexSizes = [64, 128, 256, 512]

dataset = Dataset(datasetRho, datasetPhi)

fileHandler = FileHandler()
fileHandler.setFiledir('output/results/{},{}'.format(datasetRho, datasetPhi))

summaries = summary.createSummaries(fileHandler, dataset)

texoutputdir = 'output/tex'

typedict = {
    ModelType.REFERENCE : 'reference',
    ModelType.DIRECT : 'direct',
    ModelType.VOXEL : 'voxel',
    ModelType.BOUNDARYACCURATE : 'ba',
    ModelType.HYBRID : 'hybrid'
}

voxelSummaries = summaries[ModelType.VOXEL]
interestingIndexes = []

for i, voxelSummary in enumerate(summaries[ModelType.VOXEL]):
    if voxelSummary.renderData.texSize in interestingTexSizes:
        interestingIndexes.append(i)

for i in range(ModelType._COUNT):
    if i == ModelType.REFERENCE:
        continue

    filename = '{}/stats_{},{}_{}.tex'.format(texoutputdir, datasetRho, datasetPhi, typedict[i])
    fo = open(filename, 'wb')

    for j in interestingIndexes:
        modelSummary = summaries[i][j]

        if i != ModelType.DIRECT:
            texSize = modelSummary.renderData.texSize
            fo.write('${}^2$'.format(texSize))
            fo.write(' & ')

        fo.write(str(modelSummary.renderData.renderResult.maxSamplePoints))
        fo.write(' & ')
        fo.write('{:.2f}'.format(modelSummary.max))
        fo.write(' & ')
        fo.write('{:.2f}'.format(modelSummary.mean))
        fo.write(' & ')
        fo.write('{:.2f}'.format(modelSummary.var))
        fo.write(' \\\\\n')

    fo.close()
