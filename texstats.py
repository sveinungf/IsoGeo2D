import sys

import summary
from fileio.filehandler import FileHandler
from dataset import Dataset
from modeltype import ModelType


datasetRho = int(sys.argv[1])
datasetPhi = int(sys.argv[2])

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

for i in range(ModelType._COUNT):
    if i == ModelType.REFERENCE:
        continue

    filename = '{}/stats_{},{}_{}.tex'.format(texoutputdir, datasetRho, datasetPhi, typedict[i])
    fo = open(filename, 'wb')

    for voxelSummary in voxelSummaries:
        if i != ModelType.DIRECT:
            #texSize = voxelSummary.renderData.texSize
            texSize = 128

            fo.write('${}^2$'.format(texSize))
            fo.write(' & ')

        fo.write(str(voxelSummary.renderData.renderResult.maxSamplePoints))
        fo.write(' & ')
        fo.write('{:.2f}'.format(voxelSummary.max))
        fo.write(' & ')
        fo.write('{:.2f}'.format(voxelSummary.mean))
        fo.write(' & ')
        fo.write('{:.2f}'.format(voxelSummary.var))
        fo.write(' \\\\\n')
        fo.write('\\hline\n')

    fo.close()
