import math
import numpy as np

from pattern import Location
from ray import Ray2D
from screen import Screen


def magnitude(v):
    return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))

def normalize(v):
    vmag = magnitude(v)
    return np.array([ v[i]/vmag  for i in range(len(v)) ])

def match(array, pattern):
    for i, c in enumerate(pattern):
        if c == 'Y':
            if not array[i]:
                return False
        elif c == 'N':
            if array[i]:
                return False

    return True


class Direction:
    VERTICAL = 1
    HORIZONTAL = 2
    NEGATIVE_DIAGONAL = 3
    POSITIVE_DIAGONAL = 4

    directions = [VERTICAL, HORIZONTAL, NEGATIVE_DIAGONAL, POSITIVE_DIAGONAL]


class TextureGenerator:
    def __init__(self, splineModel, width, height):
        self.boundingBox = splineModel.phiPlane.createBoundingBox()
        self.splineModel = splineModel
        self.width = width
        self.height = height

    def createScreen(self, direction):
        bb = self.boundingBox
        w = self.width
        h = self.height

        if direction == Direction.VERTICAL:
            bottom = np.array([bb.left - 1.0, bb.bottom])
            top = np.array([bb.left - 1.0, bb.top])

            screen = Screen(bottom, top, h)
        elif direction == Direction.HORIZONTAL:
            bottom = np.array([bb.right, bb.bottom - 1.0])
            top = np.array([bb.left, bb.bottom - 1.0])

            screen = Screen(bottom, top, w)
        elif direction == Direction.NEGATIVE_DIAGONAL:
            deltaWidth = (bb.right - bb.left) / w
            deltaHeight = (bb.top - bb.bottom) / h
            viewAngle = math.atan(deltaHeight / deltaWidth)
            delta = deltaWidth * math.sin(viewAngle)

            startPoint = np.array([bb.left - deltaWidth, bb.bottom - deltaHeight])

            upDir = normalize(np.array([-deltaHeight, deltaWidth]))
            top = startPoint + (h - 0.5)*delta*upDir

            downDir = normalize(np.array([deltaHeight, -deltaWidth]))
            bottom = startPoint + (w - 0.5)*delta*downDir

            screen = Screen(bottom, top, w + h - 1)
        else:
            # TODO: cleanup code

            deltaWidth = (bb.right - bb.left) / w
            deltaHeight = (bb.top - bb.bottom) / h
            viewAngle = math.atan(deltaHeight / deltaWidth)
            delta = deltaWidth * math.sin(viewAngle)

            startPoint = np.array([bb.left - deltaWidth, bb.top + deltaHeight])

            dir = normalize(np.array([deltaHeight, deltaWidth]))
            top = startPoint + (w - 0.5)*delta*dir
            bottom = startPoint - (h - 0.5)*delta*dir

            screen = Screen(bottom, top, w + h - 1)

        return screen

    def createSamplingRays(self, screen):
        rays = []

        for pixel in screen.pixels:
            eye = pixel - screen.viewDir
            samplingRay = Ray2D(eye, pixel, 10, 0)
            rays.append(samplingRay)

        return rays

    def findIntersections(self, ray):
        phiPlane = self.splineModel.phiPlane
        return phiPlane.findTwoIntersections(ray)

    def generate(self, boundingBox):
        h = self.height
        w = self.width
        phiPlane = self.splineModel.phiPlane
        rho = self.splineModel.rho

        screenSamplingRays = []

        for direction in Direction.directions:
            screen = self.createScreen(direction)
            screenSamplingRays.append(self.createSamplingRays(screen))

        samplingScalars = np.ones((h + 2, w + 2)) * -1
        indicators = np.ones((h + 2, w + 2)) * -1

        paramPoints = []
        geomPoints = []

        #vScreen = self.createScreen(Direction.VERTICAL)
        hSamplingRays = self.createSamplingRays(self.createScreen(Direction.VERTICAL))
        vSamplingRays = self.createSamplingRays(self.createScreen(Direction.HORIZONTAL))
        ndSamplingRays = self.createSamplingRays(self.createScreen(Direction.NEGATIVE_DIAGONAL))
        pdSamplingRays = self.createSamplingRays(self.createScreen(Direction.POSITIVE_DIAGONAL))

        # NB: ONLY FOR HORIZONTAL
        rayCount = self.height
        samplingsPerRay = self.width
        bb = boundingBox
        xDelta = float(bb.getWidth())/samplingsPerRay
        yDelta = float(bb.getHeight())/rayCount

        xValues = np.linspace(bb.left+xDelta/2, bb.right-xDelta/2, samplingsPerRay)
        yValues = np.linspace(bb.bottom+yDelta/2, bb.top-yDelta/2, rayCount)

        horizontalSamplingRays = []
        horizontalIntersections = []
        for y in yValues:
            samplingRay = Ray2D(np.array([bb.left-xDelta/2, y]), np.array([bb.left, y]), 10, 0)
            horizontalSamplingRays.append(samplingRay)

            horizontalIntersections.append(phiPlane.findTwoIntersections(samplingRay))

        for v, y in enumerate(yValues):
            intersections = self.findIntersections(hSamplingRays[v])
            #intersections = horizontalIntersections[v]

            if intersections is None:
                continue

            inGeomPoint = intersections[0].geomPoint
            outGeomPoint = intersections[1].geomPoint

            prevUV = intersections[0].paramPoint

            for u, x in enumerate(xValues):
                if x < inGeomPoint[0] or x > outGeomPoint[0]:
                    continue

                samplePoint = np.array([x, y])

                pApprox = phiPlane.inverseWithinTolerance(samplePoint, prevUV, 1e-5) # TODO: not hardcoded

                if pApprox is None:
                    pApprox = prevUV
                gApprox = phiPlane.evaluate(pApprox[0], pApprox[1])

                paramPoints.append(pApprox)
                geomPoints.append(gApprox)

                scalar = rho.evaluate(pApprox[0], pApprox[1])
                samplingScalars[v+1][u+1] = scalar
                indicators[v+1][u+1] = 1

                prevUV = pApprox

        origIndicators = np.copy(indicators)

        # Vertical: u -> samplingRays[-1 - u]
        # Horizontal: v -> samplingRays[v]
        # Neg.diag: u,v -> samplingRays[w-1-u+v]
        # Pos.diag: u,v -> samplingRays[u+v]

        # Extrapolation
        for j in range(h+1):
            if j < h+1:
                hIntersections = self.findIntersections(horizontalSamplingRays[j-1])
            else:
                hIntersections = None

            for i in range(w+1):
                #pdSamplingRay = pdSamplingRays[i-1 + j-1]

                neighbors = self.getNeighbours(origIndicators, i, j)

                if i != 0:
                    vIntersections = self.findIntersections(vSamplingRays[w-1-i])
                else:
                    vIntersections = None

                index = w-1-(i-1)+j-1

                if index < 0 or index > len(ndSamplingRays) - 1:
                    ndIntersections = None
                else:
                    ndSamplingRay = ndSamplingRays[w-1-(i-1)+j-1]
                    ndIntersections = self.findIntersections(ndSamplingRay)

                if origIndicators[j][i] == -1:
                    if ndIntersections is not None and (match(neighbors, '-NYN----') or match(neighbors, '-YYY----')):
                        vGeomPoint = np.array([xValues[i], yValues[j]])

                        delta = magnitude(np.array([xDelta, yDelta]))

                        self.extrapolate(ndIntersections[0], delta, vGeomPoint, rho, samplingScalars, indicators, [j,i], Location.TOPRIGHT)

                    elif i < len(xValues) and j < len(yValues) and match(neighbors, '---Y----'):
                        vGeomPoint = np.array([xValues[i], yValues[j]])

                        iParamPoint = hIntersections[0].paramPoint
                        iGeomPoint = hIntersections[0].geomPoint

                        ex = (xValues[i] - iGeomPoint[0]) / xDelta

                        #print "A={}, B={}".format(iGeomPoint[1], yValues[j])
                        #iv = vGeomPoint - iGeomPoint
                        #ex = magnitude(iv) / xDelta

                        ey = rho.evaluate(iParamPoint[0], iParamPoint[1])

                        ey0 = samplingScalars[j][i+1]

                        ey1 = ey0 + float(ey - ey0)/ex
                        samplingScalars[j][i] = ey1

                        indicators[j][i] = 1.0 - 1.0/ex


                        #self.extrapolate(hIntersections[0], xDelta, vGeomPoint, rho, samplingScalars, indicators, [j,i], Location.RIGHT)


                    elif vIntersections is not None and match(neighbors, '-Y------'):
                        vGeomPoint = np.array([xValues[i], yValues[j]])

                        self.extrapolate(vIntersections[0], yDelta, vGeomPoint, rho, samplingScalars, indicators, [j,i], Location.TOP)


        return samplingScalars, indicators

    @staticmethod
    def extrapolate(intersection, delta, vGeomPoint, rho, samplingScalars, indicators, jiE, location):
        iParamPoint = intersection.paramPoint
        iGeomPoint = intersection.geomPoint

        iv = vGeomPoint - iGeomPoint
        ivNorm = magnitude(iv) / delta

        if location == Location.TOP:
            jV = jiE[0] + 1
            iV = jiE[1]
        elif location == Location.TOPRIGHT:
            jV = jiE[0] + 1
            iV = jiE[1] + 1
        elif location == Location.RIGHT:
            jV = jiE[0]
            iV = jiE[1] + 1
        else:
            jV = None
            iV = None

        s_i = rho.evaluate(iParamPoint[0], iParamPoint[1])
        s_v = samplingScalars[jV][iV]

        s_e = s_v + (s_i - s_v) / ivNorm
        samplingScalars[jiE[0]][jiE[1]] = s_e

        indicators[jiE[0]][jiE[1]] = 1.0 - 1.0/ivNorm

    @staticmethod
    def getNeighbours(indicators, i, j):
        (rows, cols) = indicators.shape
        result = np.zeros(8, dtype=bool)

        if j > 0:
            result[Location.BOTTOM] = indicators[j-1][i] >= 0

            if i > 0:
                result[Location.BOTTOMLEFT] = indicators[j-1][i-1] >= 0
            if i < cols-1:
                result[Location.BOTTOMRIGHT] = indicators[j-1][i+1] >= 0

        if j < rows-1:
            result[Location.TOP] = indicators[j+1][i] >= 0

            if i > 0:
                result[Location.TOPLEFT] = indicators[j+1][i-1] >= 0
            if i < cols-1:
                result[Location.TOPRIGHT] = indicators[j+1][i+1] >= 0

        if i > 0:
            result[Location.LEFT] = indicators[j][i-1] >= 0
        if i < cols-1:
            result[Location.RIGHT] = indicators[j][i+1] >= 0

        return result
