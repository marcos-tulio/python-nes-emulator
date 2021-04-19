class Olc2C02():
    tbl_name = [[0x00]* 1024] * 2
    tbl_palette = [0x00] * 32

    cartridge = None

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
        pass
