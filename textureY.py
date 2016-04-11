import math
import numpy as np
from scipy import interpolate

from ray import Ray2D


class Texture2D:
    def __init__(self, texels, indicators):
        self.texels = texels
        self.indicators = indicators

        # -2 = ghost cells "are not" texels
        cols = len(texels[0]) - 2
        rows = len(texels) - 2
        self.cols = cols
        self.rows = rows

        marginX = 1.0/(2.0 * cols)
        marginY = 1.0/(2.0 * rows)

        x = np.linspace(-marginX, 1.0+marginX, cols+2)
        y = np.linspace(-marginY, 1.0+marginY, rows+2)

        self.f = interpolate.interp2d(x, y, texels, kind='linear', bounds_error=True)
        self.i = interpolate.interp2d(x, y, indicators, kind='linear', bounds_error=True)

    def fetch(self, uv):
        if self.i(uv[0], uv[1])[0] < 0.0:
            return -1

        return self.f(uv[0], uv[1])[0]

    def closest(self, uv):
        uIndex = math.floor(uv[0] * self.cols)
        vIndex = math.floor(uv[1] * self.rows)

        return self.texels[vIndex+1, uIndex+1]


def create(splineModel, width, height, tolerance, paramPlotter=None, geomPlotter=None):
    # bounding box
    # get screen (pixels based on texture size, width based on bounding box)
    # get view-rays from screen (orthogonal projection)
    # per view-ray, get intersections
    # for each point in the texture (resident and non-resident), get rays/intersections in all 4 directions (intersections may be None)
    # find neighbour pattern for current non-resident texture
    # extrapolate based on neighbour pattern and intersections

    phiPlane = splineModel.phiPlane
    rho = splineModel.rho

    bb = phiPlane.createBoundingBox()

    samplingDefault = -1

    rayCount = height
    samplingsPerRay = width

    xDelta = float(bb.getWidth())/samplingsPerRay
    yDelta = float(bb.getHeight())/rayCount

    xValues = np.linspace(bb.left+xDelta/2, bb.right-xDelta/2, samplingsPerRay)
    yValues = np.linspace(bb.bottom+yDelta/2, bb.top-yDelta/2, rayCount)

    # +2 = ghost cells
    samplingScalars = np.ones((rayCount + 2, samplingsPerRay + 2)) * samplingDefault
    indicators = np.ones((rayCount + 2, samplingsPerRay + 2)) * -1
    indicators2 = np.ones((rayCount + 2, samplingsPerRay + 2)) * -1

    geomPoints = []
    paramPoints = []

    horizontalSamplingRays = []
    horizontalIntersections = []

    verticalSamplingRays = []
    verticalIntersections = []

    fwdDiagSamplingRays = []
    fwdDiagIntersections = []

    for y in yValues:
        samplingRay = Ray2D(np.array([bb.left-xDelta/2, y]), np.array([bb.left, y]), 10, 0)
        horizontalSamplingRays.append(samplingRay)

        horizontalIntersections.append(phiPlane.findTwoIntersections(samplingRay))

    for x in xValues:
        samplingRay = Ray2D(np.array([x, bb.bottom-yDelta/2]), np.array([x, bb.bottom]), 10, 0)
        verticalSamplingRays.append(samplingRay)

        verticalIntersections.append(phiPlane.findTwoIntersections(samplingRay))

    for i in reversed(range(height - 1)):
        eye = np.array([bb.left - xDelta/2, bb.bottom - yDelta/2 + i*yDelta])
        pixel = np.array([bb.left, bb.bottom + i*yDelta])
        samplingRay = Ray2D(eye, pixel, 10, 0)
        fwdDiagSamplingRays.append(samplingRay)

        fwdDiagIntersections.append(phiPlane.findTwoIntersections(samplingRay))


    for i in range(width):
        eye = np.array([bb.left - xDelta/2 + i*xDelta, bb.bottom - yDelta/2])
        pixel = np.array([bb.left + i*xDelta, bb.bottom])
        samplingRay = Ray2D(eye, pixel, 10, 0)
        fwdDiagSamplingRays.append(samplingRay)

        fwdDiagIntersections.append(phiPlane.findTwoIntersections(samplingRay))

    for inter in fwdDiagIntersections:
        if inter is not None:
            #print inter[0].geomPoint
            pass


    for i, y in enumerate(yValues):
        intersections = horizontalIntersections[i]

        if intersections is None:
            continue

        inGeomPoint = intersections[0].geomPoint
        outGeomPoint = intersections[1].geomPoint

        prevUV = intersections[0].paramPoint

        for j, x in enumerate(xValues):
            if x < inGeomPoint[0] or x > outGeomPoint[0]:
                continue

            samplePoint = np.array([x, y])

            pApprox = phiPlane.inverseWithinTolerance(samplePoint, prevUV, tolerance)
            gApprox = phiPlane.evaluate(pApprox[0], pApprox[1])
            geomPoints.append(gApprox)

            paramPoints.append(pApprox)

            scalar = rho.evaluate(pApprox[0], pApprox[1])
            samplingScalars[i+1][j+1] = scalar
            indicators[i+1][j+1] = 1
            indicators2[i+1][j+1] = 1

            prevUV = pApprox

    # Extrapolation
    for i, intersections in enumerate(horizontalIntersections):
        if intersections is None:
            continue

        inGeomPoint = intersections[0].geomPoint
        inParamPoint = intersections[0].paramPoint

        indexFirstResident = 1
        while indicators[i+1][indexFirstResident] == -1:
            indexFirstResident += 1


        # Extrapolation (assumed gApprox == samplePoint)
        # indexFirstResident-1 pga ghost cells
        ex = (xValues[indexFirstResident-1] - inGeomPoint[0]) / xDelta

        # Skalarverdi ved intersection
        ey = rho.evaluate(inParamPoint[0], inParamPoint[1])

        # Skalarverdi ved nermeste voxelpoint
        ey0 = samplingScalars[i+1][indexFirstResident]

        # Ekstrapolert skalarverdi
        ey1 = ey0 + float(ey - ey0)/ex
        samplingScalars[i+1][indexFirstResident - 1] = ey1

        # Ekstrapolert indikator
        indicators2[i+1][indexFirstResident - 1] = 1.0 - 1.0/ex

        outGeomPoint = intersections[1].geomPoint
        outParamPoint = intersections[1].paramPoint

        indexLastResident = len(indicators[i+1]) - 2
        while indicators[i+1][indexLastResident] == -1:
            indexLastResident -= 1

        ex = (outGeomPoint[0] - xValues[indexLastResident-1]) / xDelta
        ey = rho.evaluate(outParamPoint[0], outParamPoint[1])
        ey0 = samplingScalars[i+1][indexLastResident]
        ey1 = ey0 + float(ey - ey0)/ex
        samplingScalars[i+1][indexLastResident + 1] = ey1
        indicators2[i+1][indexLastResident + 1] = 1.0 - 1.0/ex

    for i, intersections in enumerate(verticalIntersections):
        if intersections is None:
            continue

        inGeomPoint = intersections[0].geomPoint
        inParamPoint = intersections[0].paramPoint

        indexFirstResident = 1
        while indicators[indexFirstResident][i+1] == -1:
            indexFirstResident += 1

        ex = (yValues[indexFirstResident-1] - inGeomPoint[1]) / yDelta
        ey = rho.evaluate(inParamPoint[0], inParamPoint[1])
        ey0 = samplingScalars[indexFirstResident][i+1]
        ey1 = ey0 + float(ey - ey0)/ex
        samplingScalars[indexFirstResident - 1][i+1] = ey1
        indicators2[indexFirstResident - 1][i+1] = 1.0 - 1.0/ex


        outGeomPoint = intersections[1].geomPoint
        outParamPoint = intersections[1].paramPoint

        indexLastResident = len(indicators) - 2

        while indicators[indexLastResident][i+1] == -1:
            indexLastResident -= 1

        #print "outGeomPoint[1]={}".format(outGeomPoint[1])
        #print "yValues = {}".format(yValues[indexLastResident-1])

        ex = (outGeomPoint[1] - yValues[indexLastResident-1]) / yDelta
        ey = rho.evaluate(outParamPoint[0], outParamPoint[1])
        ey0 = samplingScalars[indexLastResident][i+1]
        ey1 = ey0 + float(ey - ey0)/ex
        samplingScalars[indexLastResident + 1][i+1] = ey1
        indicators2[indexLastResident + 1][i+1] = 1.0 - 1.0/ex


    if paramPlotter is not None:
        paramPlotter.plotPoints(paramPoints)

    if geomPlotter is not None:
        for samplingRay in horizontalSamplingRays:
            geomPlotter.plotViewRay(samplingRay, [-10, 10])

        geomPlotter.plotPoints(geomPoints)

    return samplingScalars, indicators2
