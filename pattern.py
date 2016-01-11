import abc


class Location:
    TOPLEFT = 0
    TOP = 1
    TOPRIGHT = 2
    RIGHT = 3
    BOTTOMRIGHT = 4
    BOTTOM = 5
    BOTTOMLEFT = 6
    LEFT = 7


class Pattern(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def extrapolate(self, textureData, u, v):
        return


class EdgePattern(Pattern):
    def __init__(self, location):
        super(EdgePattern, self).__init__()
        self.location = location

    def extrapolate(self, textureData, u, v):
        l = self.location

        if l == Location.TOPLEFT:
            return textureData[u+1][v-1]
        elif l == Location.TOP:
            return textureData[u+1][v]
        elif l == Location.TOPRIGHT:
            return textureData[u+1][v+1]
        elif l == Location.RIGHT:
            return textureData[u][v+1]
        elif l == Location.BOTTOMRIGHT:
            return textureData[u-1][v+1]
        elif l == Location.BOTTOM:
            return textureData[u-1][v]
        elif l == Location.BOTTOMLEFT:
            return textureData[u-1][v-1]
        elif l == Location.LEFT:
            return textureData[u][v-1]
        else:
            raise ValueError('Invalid location: {}'.format(l))


class CornerPattern(Pattern):
    def __init__(self, location):
        super(CornerPattern, self).__init__()
        self.location = location

    def extrapolate(self, textureData, u, v):
        l = self.location

        if l == Location.TOPLEFT:
            u2 = u + 1
            v2 = v - 1
        elif l == Location.TOPRIGHT:
            u2 = u + 1
            v2 = v + 1
        elif l == Location.BOTTOMRIGHT:
            u2 = u - 1
            v2 = v + 1
        elif l == Location.BOTTOMLEFT:
            u2 = u - 1
            v2 = v - 1
        else:
            raise ValueError('Invalid location: {}'.format(l))

        a = textureData[u][v2]
        b = textureData[u2][v]
        c = textureData[u2][v2]

        return a + b - c


class HorseshoePattern(Pattern):
    def __init__(self, location):
        super(HorseshoePattern, self).__init__()

        if location == Location.TOP:
            self.corner1 = CornerPattern(Location.TOPLEFT)
            self.corner2 = CornerPattern(Location.TOPRIGHT)
        elif location == Location.RIGHT:
            self.corner1 = CornerPattern(Location.TOPRIGHT)
            self.corner2 = CornerPattern(Location.BOTTOMRIGHT)
        elif location == Location.BOTTOM:
            self.corner1 = CornerPattern(Location.BOTTOMRIGHT)
            self.corner2 = CornerPattern(Location.BOTTOMLEFT)
        elif location == Location.LEFT:
            self.corner1 = CornerPattern(Location.BOTTOMLEFT)
            self.corner2 = CornerPattern(Location.TOPLEFT)
        else:
            raise ValueError('Invalid location: {}'.format(location))

    def extrapolate(self, textureData, u, v):
        a = self.corner1.extrapolate(textureData, u, v)
        b = self.corner2.extrapolate(textureData, u, v)

        return (a + b) / 2.0

