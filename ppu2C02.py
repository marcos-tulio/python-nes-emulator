import graphics as g
import numpy as n

class PPU2C02():
    tbl_name    = [[0x00]* 1024] * 2
    tbl_palette = [0x00] * 32

    cartridge   = None
    
    def __init__(self):
        self.scanline = 0
        self.cycle    = 0
        self.frame_complete = False

        # Sprites
        self.spr_screen   = g.Sprite(256, 240)
        self.spr_name_tbl = [ g.Sprite(256, 240), g.Sprite(256, 240)]

        # Pixels
        self.pal_screen = [
            g.Pixel(84, 84, 84)   , g.Pixel(0, 30, 116)   , g.Pixel(8, 16, 144),
            g.Pixel(48, 0, 136)   , g.Pixel(68, 0, 100)   , g.Pixel(92, 0, 48),
            g.Pixel(84, 4, 0)     , g.Pixel(60, 24, 0)    , g.Pixel(32, 42, 0),
            g.Pixel(8, 58, 0)     , g.Pixel(0, 64, 0)     , g.Pixel(0, 60, 0),
            g.Pixel(0, 50, 60)    , g.Pixel(0, 0, 0)      , g.Pixel(0, 0, 0),
            g.Pixel(0, 0, 0)      , g.Pixel(152, 150, 152), g.Pixel(8, 76, 196),
            g.Pixel(48, 50, 236)  , g.Pixel(92, 30, 228)  , g.Pixel(136, 20, 176),
            g.Pixel(160, 20, 100) , g.Pixel(152, 34, 32)  , g.Pixel(120, 60, 0),
            g.Pixel(84, 90, 0)    , g.Pixel(40, 114, 0)   , g.Pixel(8, 124, 0),
            g.Pixel(0, 118, 40)   , g.Pixel(0, 102, 120)  , g.Pixel(0, 0, 0),
            g.Pixel(0, 0, 0)      , g.Pixel(0, 0, 0)      , g.Pixel(236, 238, 236),
            g.Pixel(76, 154, 236) , g.Pixel(120, 124, 236), g.Pixel(176, 98, 236),
            g.Pixel(228, 84, 236) , g.Pixel(236, 88, 180) , g.Pixel(236, 106, 100),
            g.Pixel(212, 136, 32) , g.Pixel(160, 170, 0)  , g.Pixel(116, 196, 0),
            g.Pixel(76, 208, 32)  , g.Pixel(56, 204, 108) , g.Pixel(56, 180, 204),
            g.Pixel(60, 60, 60)   , g.Pixel(0, 0, 0)      , g.Pixel(0, 0, 0),
            g.Pixel(236, 238, 236), g.Pixel(168, 204, 236), g.Pixel(188, 188, 236),
            g.Pixel(212, 178, 236), g.Pixel(236, 174, 236), g.Pixel(236, 174, 212),
            g.Pixel(236, 180, 176), g.Pixel(228, 196, 144), g.Pixel(204, 210, 120),
            g.Pixel(180, 222, 120), g.Pixel(168, 226, 144), g.Pixel(152, 226, 180),
            g.Pixel(160, 214, 228), g.Pixel(160, 162, 160), g.Pixel(0, 0, 0),
            g.Pixel(0, 0, 0)
        ]

    def cpuRead(self, addr, isReadOnly = False):
        data = 0x00

        if addr == 0x0000:      # control
            pass
        elif addr == 0x0001:    # mask
            pass
        elif addr == 0x0002:    # status
            pass
        elif addr == 0x0003:    # OAM Address
            pass
        elif addr == 0x0004:    # OAM Data
            pass
        elif addr == 0x0005:    # Scroll
            pass
        elif addr == 0x0006:    # PPU Address
            pass
        elif addr == 0x0007:    # PPU Data
            pass

        return data

    def cpuWrite(self, addr, data):
        if addr == 0x0000:      # control
            pass
        elif addr == 0x0001:    # mask
            pass
        elif addr == 0x0002:    # status
            pass
        elif addr == 0x0003:    # OAM Address
            pass
        elif addr == 0x0004:    # OAM Data
            pass
        elif addr == 0x0005:    # Scroll
            pass
        elif addr == 0x0006:    # PPU Address
            pass
        elif addr == 0x0007:    # PPU Data
            pass

    def ppuRead(self, addr, isReadOnly = False):
        data = 0x00
        addr &= 0x3FFF

        if self.cartridge.ppuRead(addr, isReadOnly):
            pass

        return data

    def ppuWrite(self, addr, data):
        addr &= 0x3FFF

        if self.cartridge.ppuWrite(addr, data):
            pass      

    def connectCartridge(self, cartridge):
        self.cartridge = cartridge

    def clock(self):
        # Fake some noise for now
        fake = 0x30
        if int((n.random.rand() * 15)) % 2: fake = 0x3F

        self.spr_screen.setPixel(self.cycle - 1, self.scanline, self.pal_screen[fake])

        # Advance renderer - it never stops, it's relentless
        self.cycle += 1

        if (self.cycle >= 341):
            self.cycle = 0
            self.scanline += 1

            if (self.scanline >= 261):
                self.scanline = -1
                self.frame_complete = True