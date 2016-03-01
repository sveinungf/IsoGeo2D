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

voxelSummaries = summaries[ModelType.VOXEL]

fo = open('{}/stats_{},{}_voxel.tex'.format(texoutputdir, datasetRho, datasetPhi), 'wb')

for voxelSummary in voxelSummaries:
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
