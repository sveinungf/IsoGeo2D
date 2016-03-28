import math
import numpy as np

from ray import Ray2D
from screen import Screen


def magnitude(v):
    return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))

def normalize(v):
    vmag = magnitude(v)
    return np.array([ v[i]/vmag  for i in range(len(v)) ])


class Direction:
    VERTICAL = 1
    HORIZONTAL = 2
    NEGATIVE_DIAGONAL = 3
    POSITIVE_DIAGONAL = 4


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

            screen = Screen(bottom, top, w + h + 1)

        return screen

    def createSamplingRays(self, screen):
        rays = []

        for pixel in screen.pixels:
            eye =