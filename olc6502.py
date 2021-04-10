from enum import IntEnum

class FLAG(IntEnum):
    C = (1 << 0)
    Z = (1 << 1)
    I = (1 << 2)
    D = (1 << 3)
    B = (1 << 4)
    U = (1 << 5)
    V = (1 << 6)
    N = (1 << 7) 

class FLAG_ADDR_MODE(IntEnum):
    IMM = 0
    REL = 1
    ABS = 2
    IZX = 3
    IZY = 4 
    IMP = 5

class Opcode():
    def __init__(self, name, addr_mode, cycles):
        self.name = name
        self.addr_mode = addr_mode
        self.cycles = cycles

class Olc6502():
    def __init__(self):
        self.bus = None

        # Registers
        self.acc    = 0x00
        self.reg_x  = 0x00
        self.reg_y  = 0x00
        self.stack  = 0x00
        self.pcount = 0x0000
        self.status = 0x00

        # Assisstive variables to facilitate emulation
        self.fetched     = 0x00
        self.addr_abs    = 0x0000
        self.addr_rel    = 0x00
        self.opcode      = 0x00
        self.cycles      = 0
        self.clock_count = 0

        self.lookup = [
            Opcode("BRK", FLAG_ADDR_MODE.IMM, 7)
        ]

    def clock(self):
        if self.cycles <= 0:
            self.opcode = self.bus.read(self.pcount)
            self.setFlag(FLAG.U, True)            
            self.pcount += 1
            self.cycles = self.lookup[self.opcode].cycles

        self.clock_count += 1
        self.cycles -= 1

    def connectBus(self, bus):
        self.bus = bus

    def setFlag(self, flag, value):
        if value:
            self.status |= flag
            return
        
        self.status &= ~flag

