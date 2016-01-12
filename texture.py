import math
import numpy as np
from scipy import interpolate

from pattern import CornerPattern, EdgePattern, HorseshoePattern, Location


def match(array, pattern):
    for i, c in enumerate(pattern):
        if c == 'T':
            if not array[i]:
                return False
        elif c == 'F':
            if array[i]:
                return False

    return True


class Texture2D:
    def __init__(self, scalarMatrix):
        RESIDENT = 0
        NONRESIDENT = -1

        cols = len(scalarMatrix[0])
        rows = len(scalarMatrix)
        self.cols = cols
        self.rows = rows

        indicators = np.empty_like(scalarMatrix)

        for u in range(rows):
            for v in range(cols):
                if scalarMatrix[u][v] == -1:
                    indicators[u][v] = NONRESIDENT
                elif not self.__hasNeighbour(scalarMatrix, u, v):
                    indicators[u][v] = NONRESIDENT
                else:
                    indicators[u][v] = RESIDENT

        marginX = 1.0/(2.0 * cols)
        marginY = 1.0/(2.0 * rows)

        self.indicators = indicators

        for u in range(rows):
            for v in range(cols):
                if indicators[u][v] == NONRESIDENT and self.__hasNeighbourInclDiag(indicators, u, v):
                    if scalarMatrix[u][v] == -1:
                        self.__extrapolate(scalarMatrix, indicators, u, v)
        
        data = scalarMatrix
        data = np.vstack((data[0], data))
        data = np.vstack((data, data[-1]))
        data = np.column_stack((data[:, 0], data))
        data = np.column_stack((data, data[:, -1]))
        self.textureData = data

        x = np.linspace(-marginX, 1.0+marginX, cols+2)
        y = np.linspace(-marginY, 1.0+marginY, rows+2)
        
        self.f = interpolate.interp2d(x, y, data, kind='linear', bounds_error=True)

    @staticmethod
    def __hasNeighbour(matrix, u, v):
        (rows, cols) = matrix.shape

        if u > 0 and matrix[u-1][v] >= 0:
            return True
        if u < rows-1 and matrix[u+1][v] >= 0:
            return True
        if v > 0 and matrix[u][v-1] >= 0:
            return True
        if v < cols-1 and matrix[u][v+1] >= 0:
            return True

        return False

    @classmethod
    def __hasNeighbourInclDiag(cls, matrix, u, v):
        (rows, cols) = matrix.shape

        if cls.__hasNeighbour(matrix, u, v):
            return True

        if u > 0:
            if v > 0 and matrix[u-1][v-1] >= 0:
                return True
            if v < cols-1 and matrix[u-1][v+1] >= 0:
                return True
        if u < rows-1:
            if v > 0 and matrix[u+1][v-1] >= 0:
                return True
            if v < cols-1 and matrix[u+1][v+1] >= 0:
                return True

        return False

    @classmethod
    def __extrapolate(cls, textureData, indicators, u, v):
        neighbours = cls.__neighbours(indicators, u, v)
        pattern = cls.__neighbourPattern(neighbours)
        textureData[u][v] = pattern.extrapolate(textureData, u, v)

    @staticmethod
    def __neighbourPattern(neighbours):
        result = None
        n = neighbours

        if match(n, 'TTTT?FFT') or match(n, 'TTTTFF?T'):
            result = HorseshoePattern(Location.TOP)
        elif match(n, '?TTTTTFF') or match(n, 'FTTTTT?F'):
            result = HorseshoePattern(Location.RIGHT)
        elif match(n, '?FFTTTTT') or match(n, 'FF?TTTTT'):
            result = HorseshoePattern(Location.BOTTOM)
        elif match(n, 'TT?FFTTT') or match(n, 'TTFF?TTT'):
            result = HorseshoePattern(Location.LEFT)
        elif match(n, 'TT?FFF?T'):
            result = CornerPattern(Location.TOPLEFT)
        elif match(n, '?TTT?FFF'):
            result = CornerPattern(Location.TOPRIGHT)
        elif match(n, 'FF?TTT?F'):
            result = CornerPattern(Location.BOTTOMRIGHT)
        elif match(n, '?FFF?TTT'):
            result = CornerPattern(Location.BOTTOMLEFT)
        elif match(n, '?T?FFFFF'):
            result = EdgePattern(Location.TOP)
        elif match(n, 'FF?T?FFF'):
            result = EdgePattern(Location.RIGHT)
        elif match(n, 'FFFF?T?F'):
            result = EdgePattern(Location.BOTTOM)
        elif match(n, '?FFFFF?T'):
            result = EdgePattern(Location.LEFT)
        elif match(n, 'TFFFFFFF'):
            result = EdgePattern(Location.TOPLEFT)
        elif match(n, 'FFTFFFFF'):
            result = EdgePattern(Location.TOPRIGHT)
        elif match(n, 'FFFFTFFF'):
            result = EdgePattern(Location.BOTTOMRIGHT)
        elif match(n, 'FFFFFFTF'):
            result = EdgePattern(Location.BOTTOMLEFT)

        if result is None:
            raise ValueError('No neighbour pattern for: {}'.format(neighbours))

        return result

    @staticmethod
    def __neighbours(indicators, u, v):
        (rows, cols) = indicators.shape
        result = np.zeros(8, dtype=bool)

        if u > 0:
            result[Location.BOTTOM] = indicators[u-1][v] >= 0

            if v > 0:
                result[Location.BOTTOMLEFT] = indicators[u-1][v-1] >= 0
            if v < cols-1:
                result[Location.BOTTOMRIGHT] = indicators[u-1][v+1] >= 0

        if u < rows-1:
            result[Location.TOP] = indicators[u+1][v] >= 0

            if v > 0:
                result[Location.TOPLEFT] = indicators[u+1][v-1] >= 0
            if v < cols-1:
                result[Location.TOPRIGHT] = indicators[u+1][v+1] >= 0

        if v > 0:
            result[Location.LEFT] = indicators[u][v-1] >= 0
        if v < cols-1:
            result[Location.RIGHT] = indicators[u][v+1] >= 0

        return result

    def fetch(self, uv):
        if self.closest(uv) == -1:
            return -1

        uIndex = math.floor(uv[0] * self.cols)
        vIndex = math.floor(uv[1] * self.rows)

        uIndex = uIndex if uIndex < (self.cols-1) else (self.cols-1)
        vIndex = vIndex if vIndex < (self.rows-1) else (self.rows-1)

        if self.indicators[vIndex, uIndex] < 0.0:
            return -1
        
        return self.f(uv[0], uv[1])[0]

    def closest(self, uv):
        uIndex = math.floor(uv[0] * self.cols)
        vIndex = math.floor(uv[1] * self.rows)
        
        return self.textureData[vIndex+1, uIndex+1]
