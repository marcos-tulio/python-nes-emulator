from enum import IntEnum

default_alpha = 0xFF
default_pixel = (default_alpha << 24)

class Pixel():
    class MODE(IntEnum):
        NORMAL = 0
        MASK = 1
        ALPHA = 2
        CUSTOM = 3

    def __init__(self, r, g, b, a = default_alpha):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

class Sprite():
    class MODE(IntEnum):
        NORMAL   = 0
        PERIODIC = 1

    class FLIP(IntEnum):
        NONE  = 0
        HORIZ = 1
        VERT  = 2

    mode_sample = MODE.NORMAL
    col_data = []

    def __init__(self, width, height):
        self.width = width
        self.height = height

        '''
        self.col_data = [None] * (width * height)

        for x in range(len(self.col_data)):
            self.col_data[x] = Pixel(255, 0, 0)
        '''
        
        self.col_data = [Pixel(255, 0, 0, 1)] * (width * height)

    def getPixel(self, x, y):
        if self.mode_sample == self.MODE.NORMAL:
            if (x >= 0 and x < self.width and y >= 0 and y < self.height):
                return self.col_data[y * self.width + x]

            return Pixel(0, 0, 0, 0)

        return self.col_data[abs(y % self.height) * self.width + abs(x % self.width)]

    def setPixel(self, x, y, pixel):
        if (x >= 0 and x < self.width and y >= 0 and y < self.height):
            self.col_data[y * self.width + x] = pixel

            return True

        return False
