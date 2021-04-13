import olc6502_constants as CONSTANTS

class OP():
    def __init__(self, operate, addr_mode, cycles):
        self.operate = operate
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
            OP(self.BRK, self.IMM, 7 ),
            OP(self.ORA, self.IZX, 6 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 8 ),
            OP(self.NOP, self.IMP, 3 ),
            OP(self.ORA, self.ZP0, 3 ),
            OP(self.ASL, self.ZP0, 5 ),
            OP(self.XXX, self.IMP, 5 ),
            OP(self.PHP, self.IMP, 3 ),
            OP(self.ORA, self.IMM, 2 ),
            OP(self.ASL, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.NOP, self.IMP, 4 ),
            OP(self.ORA, self.ABS, 4 ),
            OP(self.ASL, self.ABS, 6 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.BPL, self.REL, 2 ),
            OP(self.ORA, self.IZY, 5 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 8 ),
            OP(self.NOP, self.IMP, 4 ),
            OP(self.ORA, self.ZPX, 4 ),
            OP(self.ASL, self.ZPX, 6 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.CLC, self.IMP, 2 ),
            OP(self.ORA, self.ABY, 4 ),
            OP(self.NOP, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 7 ),
            OP(self.NOP, self.IMP, 4 ),
            OP(self.ORA, self.ABX, 4 ),
            OP(self.ASL, self.ABX, 7 ),
            OP(self.XXX, self.IMP, 7 ),
            OP(self.JSR, self.ABS, 6 ),
            OP(self.AND, self.IZX, 6 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 8 ),
            OP(self.BIT, self.ZP0, 3 ),
            OP(self.AND, self.ZP0, 3 ),
            OP(self.ROL, self.ZP0, 5 ),
            OP(self.XXX, self.IMP, 5 ),
            OP(self.PLP, self.IMP, 4 ),
            OP(self.AND, self.IMM, 2 ),
            OP(self.ROL, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.BIT, self.ABS, 4 ),
            OP(self.AND, self.ABS, 4 ),
            OP(self.ROL, self.ABS, 6 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.BMI, self.REL, 2 ),
            OP(self.AND, self.IZY, 5 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 8 ),
            OP(self.NOP, self.IMP, 4 ),
            OP(self.AND, self.ZPX, 4 ),
            OP(self.ROL, self.ZPX, 6 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.SEC, self.IMP, 2 ),
            OP(self.AND, self.ABY, 4 ),
            OP(self.NOP, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 7 ),
            OP(self.NOP, self.IMP, 4 ),
            OP(self.AND, self.ABX, 4 ),
            OP(self.ROL, self.ABX, 7 ),
            OP(self.XXX, self.IMP, 7 ),
            OP(self.RTI, self.IMP, 6 ),
            OP(self.EOR, self.IZX, 6 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 8 ),
            OP(self.NOP, self.IMP, 3 ),
            OP(self.EOR, self.ZP0, 3 ),
            OP(self.LSR, self.ZP0, 5 ),
            OP(self.XXX, self.IMP, 5 ),
            OP(self.PHA, self.IMP, 3 ),
            OP(self.EOR, self.IMM, 2 ),
            OP(self.LSR, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.JMP, self.ABS, 3 ),
            OP(self.EOR, self.ABS, 4 ),
            OP(self.LSR, self.ABS, 6 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.BVC, self.REL, 2 ),
            OP(self.EOR, self.IZY, 5 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 8 ),
            OP(self.NOP, self.IMP, 4 ),
            OP(self.EOR, self.ZPX, 4 ),
            OP(self.LSR, self.ZPX, 6 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.CLI, self.IMP, 2 ),
            OP(self.EOR, self.ABY, 4 ),
            OP(self.NOP, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 7 ),
            OP(self.NOP, self.IMP, 4 ),
            OP(self.EOR, self.ABX, 4 ),
            OP(self.LSR, self.ABX, 7 ),
            OP(self.XXX, self.IMP, 7 ),
            OP(self.RTS, self.IMP, 6 ),
            OP(self.ADC, self.IZX, 6 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 8 ),
            OP(self.NOP, self.IMP, 3 ),
            OP(self.ADC, self.ZP0, 3 ),
            OP(self.ROR, self.ZP0, 5 ),
            OP(self.XXX, self.IMP, 5 ),
            OP(self.PLA, self.IMP, 4 ),
            OP(self.ADC, self.IMM, 2 ),
            OP(self.ROR, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.JMP, self.IND, 5 ),
            OP(self.ADC, self.ABS, 4 ),
            OP(self.ROR, self.ABS, 6 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.BVS, self.REL, 2 ),
            OP(self.ADC, self.IZY, 5 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 8 ),
            OP(self.NOP, self.IMP, 4 ),
            OP(self.ADC, self.ZPX, 4 ),
            OP(self.ROR, self.ZPX, 6 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.SEI, self.IMP, 2 ),
            OP(self.ADC, self.ABY, 4 ),
            OP(self.NOP, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 7 ),
            OP(self.NOP, self.IMP, 4 ),
            OP(self.ADC, self.ABX, 4 ),
            OP(self.ROR, self.ABX, 7 ),
            OP(self.XXX, self.IMP, 7 ),
            OP(self.NOP, self.IMP, 2 ),
            OP(self.STA, self.IZX, 6 ),
            OP(self.NOP, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.STY, self.ZP0, 3 ),
            OP(self.STA, self.ZP0, 3 ),
            OP(self.STX, self.ZP0, 3 ),
            OP(self.XXX, self.IMP, 3 ),
            OP(self.DEY, self.IMP, 2 ),
            OP(self.NOP, self.IMP, 2 ),
            OP(self.TXA, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.STY, self.ABS, 4 ),
            OP(self.STA, self.ABS, 4 ),
            OP(self.STX, self.ABS, 4 ),
            OP(self.XXX, self.IMP, 4 ),
            OP(self.BCC, self.REL, 2 ),
            OP(self.STA, self.IZY, 6 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.STY, self.ZPX, 4 ),
            OP(self.STA, self.ZPX, 4 ),
            OP(self.STX, self.ZPY, 4 ),
            OP(self.XXX, self.IMP, 4 ),
            OP(self.TYA, self.IMP, 2 ),
            OP(self.STA, self.ABY, 5 ),
            OP(self.TXS, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 5 ),
            OP(self.NOP, self.IMP, 5 ),
            OP(self.STA, self.ABX, 5 ),
            OP(self.XXX, self.IMP, 5 ),
            OP(self.XXX, self.IMP, 5 ),
            OP(self.LDY, self.IMM, 2 ),
            OP(self.LDA, self.IZX, 6 ),
            OP(self.LDX, self.IMM, 2 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.LDY, self.ZP0, 3 ),
            OP(self.LDA, self.ZP0, 3 ),
            OP(self.LDX, self.ZP0, 3 ),
            OP(self.XXX, self.IMP, 3 ),
            OP(self.TAY, self.IMP, 2 ),
            OP(self.LDA, self.IMM, 2 ),
            OP(self.TAX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.LDY, self.ABS, 4 ),
            OP(self.LDA, self.ABS, 4 ),
            OP(self.LDX, self.ABS, 4 ),
            OP(self.XXX, self.IMP, 4 ),
            OP(self.BCS, self.REL, 2 ),
            OP(self.LDA, self.IZY, 5 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 5 ),
            OP(self.LDY, self.ZPX, 4 ),
            OP(self.LDA, self.ZPX, 4 ),
            OP(self.LDX, self.ZPY, 4 ),
            OP(self.XXX, self.IMP, 4 ),
            OP(self.CLV, self.IMP, 2 ),
            OP(self.LDA, self.ABY, 4 ),
            OP(self.TSX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 4 ),
            OP(self.LDY, self.ABX, 4 ),
            OP(self.LDA, self.ABX, 4 ),
            OP(self.LDX, self.ABY, 4 ),
            OP(self.XXX, self.IMP, 4 ),
            OP(self.CPY, self.IMM, 2 ),
            OP(self.CMP, self.IZX, 6 ),
            OP(self.NOP, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 8 ),
            OP(self.CPY, self.ZP0, 3 ),
            OP(self.CMP, self.ZP0, 3 ),
            OP(self.DEC, self.ZP0, 5 ),
            OP(self.XXX, self.IMP, 5 ),
            OP(self.INY, self.IMP, 2 ),
            OP(self.CMP, self.IMM, 2 ),
            OP(self.DEX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.CPY, self.ABS, 4 ),
            OP(self.CMP, self.ABS, 4 ),
            OP(self.DEC, self.ABS, 6 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.BNE, self.REL, 2 ),
            OP(self.CMP, self.IZY, 5 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 8 ),
            OP(self.NOP, self.IMP, 4 ),
            OP(self.CMP, self.ZPX, 4 ),
            OP(self.DEC, self.ZPX, 6 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.CLD, self.IMP, 2 ),
            OP(self.CMP, self.ABY, 4 ),
            OP(self.NOP, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 7 ),
            OP(self.NOP, self.IMP, 4 ),
            OP(self.CMP, self.ABX, 4 ),
            OP(self.DEC, self.ABX, 7 ),
            OP(self.XXX, self.IMP, 7 ),
            OP(self.CPX, self.IMM, 2 ),
            OP(self.SBC, self.IZX, 6 ),
            OP(self.NOP, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 8 ),
            OP(self.CPX, self.ZP0, 3 ),
            OP(self.SBC, self.ZP0, 3 ),
            OP(self.INC, self.ZP0, 5 ),
            OP(self.XXX, self.IMP, 5 ),
            OP(self.INX, self.IMP, 2 ),
            OP(self.SBC, self.IMM, 2 ),
            OP(self.NOP, self.IMP, 2 ),
            OP(self.SBC, self.IMP, 2 ),
            OP(self.CPX, self.ABS, 4 ),
            OP(self.SBC, self.ABS, 4 ),
            OP(self.INC, self.ABS, 6 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.BEQ, self.REL, 2 ),
            OP(self.SBC, self.IZY, 5 ),
            OP(self.XXX, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 8 ),
            OP(self.NOP, self.IMP, 4 ),
            OP(self.SBC, self.ZPX, 4 ),
            OP(self.INC, self.ZPX, 6 ),
            OP(self.XXX, self.IMP, 6 ),
            OP(self.SED, self.IMP, 2 ),
            OP(self.SBC, self.ABY, 4 ),
            OP(self.NOP, self.IMP, 2 ),
            OP(self.XXX, self.IMP, 7 ),
            OP(self.NOP, self.IMP, 4 ),
            OP(self.SBC, self.ABX, 4 ),
            OP(self.INC, self.ABX, 7 ),
            OP(self.XXX, self.IMP, 7 ),
        ]

    def reset(self):
        self.addr_abs = 0xFFFC
        
        lo = self.bus.read(self.addr_abs + 0)
        hi = self.bus.read(self.addr_abs + 1)

        self.pcount = (hi << 8) | lo

        self.acc   = 0
        self.reg_x = 0
        self.reg_y = 0
        self.stack = 0xFD
        self.status = 0x00 | CONSTANTS.OLC6502_FLAG.U

        self.addr_rel = 0x0000
        self.addr_abs = 0x0000
        self.fetched = 0x00

        self.cycles = 8

    def irq(self):
        if (self.getFlag(CONSTANTS.OLC6502_FLAG.I) == 0):
            self.bus.write(0x0100 + self.stack, (self.pcount >> 8) & 0x00FF)
            self.stack -= 1

            self.bus.write(0x0100 + self.stack, self.pcount & 0x00FF)
            self.stack -= 1

            self.setFlag(CONSTANTS.OLC6502_FLAG.B, 0)
            self.setFlag(CONSTANTS.OLC6502_FLAG.U, 1)
            self.setFlag(CONSTANTS.OLC6502_FLAG.I, 1)

            self.bus.write(0x0100 + self.stack, self.status)
            self.stack -= 1

            self.addr_abs = 0xFFFE
            lo = self.bus.read(self.addr_abs + 0)
            hi = self.bus.read(self.addr_abs + 1)
            self.pcount = (hi << 8) | lo

            self.cycles = 7

    def nmi(self):
        self.bus.write(0x0100 + self.stack, (self.pcount >> 8) & 0x00FF)
        self.stack -= 1

        self.bus.write(0x0100 + self.stack, self.pcount & 0x00FF)
        self.stack -= 1

        self.setFlag(CONSTANTS.OLC6502_FLAG.B, 0)
        self.setFlag(CONSTANTS.OLC6502_FLAG.U, 1)
        self.setFlag(CONSTANTS.OLC6502_FLAG.I, 1)

        self.bus.write(0x0100 + self.stack, self.status)
        self.stack -= 1

        self.addr_abs = 0xFFFA
        lo = self.bus.read(self.addr_abs + 0)
        hi = self.bus.read(self.addr_abs + 1)
        self.pcount = (hi << 8) | lo

        self.cycles = 8

    def clock(self):
        if self.cycles <= 0:
            self.opcode = self.bus.read(self.pcount)
            self.setFlag(CONSTANTS.OLC6502_FLAG.U, True)            
            self.pcount += 1
            self.cycles = self.lookup[self.opcode].cycles

            additional_cycle1 = (self.lookup[self.opcode].addr_mode)()
            additional_cycle2 = (self.lookup[self.opcode].operate)()
            
            self.cycles += (additional_cycle1 & additional_cycle2)
            self.setFlag(CONSTANTS.OLC6502_FLAG.U, True)

        self.clock_count += 1
        self.cycles -= 1

    def connectBus(self, bus):
        self.bus = bus

    def setFlag(self, flag, value):
        if value:
            self.status |= flag
            return
        
        self.status &= ~flag

    def getFlag(self, f):
        if (self.status & f) > 0:
            return 1

        return 0

    # Addrs modes
    def IMP(self):
        self.fetched = self.acc
        return 0

    def IMM(self):
        self.pcount += 1
        self.addr_abs = self.pcount
        return 0

    def ZP0(self):
        self.addr_abs = self.bus.read(self.pcount)	
        self.pcount += 1
        self.addr_abs &= 0x00FF
        return 0

    def ZPX(self):
        self.addr_abs = (self.bus.read(self.pcount) + self.reg_x)
        self.pcount += 1
        self.addr_abs &= 0x00FF
        return 0

    def ZPY(self):
        self.addr_abs = (self.bus.read(self.pcount) + self.reg_y)
        self.pcount += 1
        self.addr_abs &= 0x00FF
        return 0

    def REL(self):
        self.addr_rel = self.bus.read(self.pcount)
        self.pcount += 1

        if self.addr_rel & 0x80:
            self.addr_rel |= 0xFF00

        return 0

    def ABS(self):
        lo = self.bus.read(self.pcount)
        self.pcount += 1

        hi = self.bus.read(self.pcount)
        self.pcount += 1

        self.addr_abs = (hi << 8) | lo

        return 0

    def ABX(self):
        lo = self.bus.read(self.pcount)
        self.pcount += 1
        
        hi = self.bus.read(self.pcount)
        self.pcount += 1

        self.addr_abs = (hi << 8) | lo
        self.addr_abs += self.reg_x

        if ((self.addr_abs & 0xFF00) != (hi << 8)):
            return 1

        return 0

    def ABY(self):
        lo = self.bus.read(self.pcount)
        self.pcount += 1
        
        hi = self.bus.read(self.pcount)
        self.pcount += 1

        self.addr_abs = (hi << 8) | lo
        self.addr_abs += self.reg_y

        if ((self.addr_abs & 0xFF00) != (hi << 8)):
            return 1

        return 0

    def IND(self):
        ptr_lo = self.bus.read(self.pcount)
        self.pcount += 1

        ptr_hi = self.bus.read(self.pcount)
        self.pcount += 1

        ptr = (ptr_hi << 8) | ptr_lo

        if (ptr_lo == 0x00FF): # Simulate page boundary hardware bug
            self.addr_abs = (self.bus.read(ptr & 0xFF00) << 8) | self.bus.read(ptr + 0)
        else:
            self.addr_abs = (self.bus.read(ptr + 1) << 8) | self.bus.read(ptr + 0)

        return 0

    def IZX(self):
        t = self.bus.read(self.pcount)
        self.pcount += 1

        lo = self.bus.read((t + self.reg_x) & 0x00FF)
        hi = self.bus.read((t + self.reg_x + 1) & 0x00FF)

        self.addr_abs = (hi << 8) | lo

        return 0

    def IZY(self):
        t = self.bus.read(self.pcount)
        self.pcount += 1

        lo = self.bus.read(t & 0x00FF)
        hi = self.bus.read((t + 1) & 0x00FF)

        self.addr_abs = (hi << 8) | lo
        self.addr_abs += self.reg_y

        if ((self.addr_abs & 0xFF00) != (hi << 8)):
            return 1

        return 0

    def fetch(self):
        if not (self.lookup[self.opcode].addr_mode == self.IMP):
            self.fetched = self.bus.read(self.addr_abs)

        return self.fetched

    ################################################
    # OPCODES
    #################################################
    def ADC(self):
        self.fetch()
        
        temp = self.acc + self.fetched + self.getFlag(CONSTANTS.OLC6502_FLAG.C)
        
        self.setFlag(CONSTANTS.OLC6502_FLAG.C, temp > 255)
        
        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, (temp & 0x00FF) == 0)
        
        self.setFlag(CONSTANTS.OLC6502_FLAG.V, (~(self.acc ^ self.fetched) & (self.acc ^ temp)) & 0x0080)
        
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, temp & 0x80)
        
        self.acc = temp & 0x00FF
        
        return 1
    
    def SBC(self):
        self.fetch()

        value = self.fetched ^ 0x00FF

        temp = self.acc + value + self.getFlag(CONSTANTS.OLC6502_FLAG.C)

        self.setFlag(CONSTANTS.OLC6502_FLAG.C, temp & 0xFF00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, ((temp & 0x00FF) == 0))
        self.setFlag(CONSTANTS.OLC6502_FLAG.V, (temp ^ self.acc) & (temp ^ value) & 0x0080)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, temp & 0x0080)

        self.acc = temp & 0x00FF

        return 1

    def AND(self):    
        self.fetch()
        self.acc = self.acc & self.fetched

        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.acc == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.acc & 0x80)

        return 1
    
    def ASL(self):    
        self.fetch()
        temp = self.fetched << 1

        self.setFlag(CONSTANTS.OLC6502_FLAG.C, (temp & 0xFF00) > 0)
        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, (temp & 0x00FF) == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, temp & 0x80)

        if (self.lookup[self.opcode].addrmode == self.IMP):
            self.acc = temp & 0x00FF
        else:
            self.bus.write(self.addr_abs, temp & 0x00FF)

        return 0
    
    def BCC(self):    
        if (self.getFlag(CONSTANTS.OLC6502_FLAG.C) == 0):
        
            self.cycles += 1
            self.addr_abs = self.pcount + self.addr_rel
            
            if((self.addr_abs & 0xFF00) != (self.pcount & 0xFF00)):
                self.cycles += 1
            
            self.pcount = self.addr_abs
        
        return 0
    
    def BCS(self):    
        if (self.getFlag(CONSTANTS.OLC6502_FLAG.C) == 1):
        
            self.cycles += 1
            self.addr_abs = self.pcount + self.addr_rel

            if ((self.addr_abs & 0xFF00) != (self.pcount & 0xFF00)):
                self.cycles += 1

            self.pcount = self.addr_abs
        
        return 0
    
    def BEQ(self):    
        if (self.getFlag(CONSTANTS.OLC6502_FLAG.Z) == 1):
        
            self.cycles += 1
            self.addr_abs = self.pcount + self.addr_rel

            if ((self.addr_abs & 0xFF00) != (self.pcount & 0xFF00)):
                self.cycles += 1

            self.pcount = self.addr_abs
        
        return 0

    def BIT(self):    
        self.fetch()
        temp = self.acc & self.fetched

        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, (temp & 0x00FF) == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.fetched & (1 << 7))
        self.setFlag(CONSTANTS.OLC6502_FLAG.V, self.fetched & (1 << 6))

        return 0
    
    def BMI(self):    
        if (self.getFlag(CONSTANTS.OLC6502_FLAG.N) == 1):
        
            self.cycles += 1
            self.addr_abs = self.pcount + self.addr_rel

            if ((self.addr_abs & 0xFF00) != (self.pcount & 0xFF00)):
                self.cycles += 1

            self.pcount = self.addr_abs
        
        return 0
    
    def BNE(self):    
        if (self.getFlag(CONSTANTS.OLC6502_FLAG.Z) == 0):        
            self.cycles += 1
            self.addr_abs = self.pcount + self.addr_rel

            if ((self.addr_abs & 0xFF00) != (self.pcount & 0xFF00)):
                self.cycles += 1

            self.pcount = self.addr_abs
        
        return 0
    
    def BPL(self):    
        if (self.getFlag(CONSTANTS.OLC6502_FLAG.N) == 0):
        
            self.cycles += 1
            self.addr_abs = self.pcount + self.addr_rel

            if ((self.addr_abs & 0xFF00) != (self.pcount & 0xFF00)):
                self.cycles += 1

            self.pcount = self.addr_abs
        
        return 0
    
    def BRK(self):    
        self.pcount += 1        
        self.setFlag(CONSTANTS.OLC6502_FLAG.I, 1)

        self.bus.write(0x0100 + self.stack, (self.pcount >> 8) & 0x00FF)
        self.stack -= 1

        self.bus.write(0x0100 + self.stack, self.pcount & 0x00FF)
        self.stack -= 1

        self.setFlag(CONSTANTS.OLC6502_FLAG.B, 1)
        self.bus.write(0x0100 + self.stack, self.status)

        self.stack -= 1
        self.setFlag(CONSTANTS.OLC6502_FLAG.B, 0)

        self.pcount = read(0xFFFE) | (read(0xFFFF) << 8)
        return 0

    def BVC(self):
        if (self.getFlag(CONSTANTS.OLC6502_FLAG.V) == 0):
            self.cycles += 1
            self.addr_abs = self.pcount + self.addr_rel

            if ((self.addr_abs & 0xFF00) != (self.pcount & 0xFF00)):
                self.cycles += 1

            self.pcount = self.addr_abs
        return 0

    def BVS(self):
        if (self.getFlag(CONSTANTS.OLC6502_FLAG.V) == 1):
            self.cycles += 1
            self.addr_abs = self.pcount + self.addr_rel

            if ((self.addr_abs & 0xFF00) != (self.pcount & 0xFF00)):
                self.cycles += 1

            self.pcount = self.addr_abs
        return 0

    def CLC(self):
        self.setFlag(CONSTANTS.OLC6502_FLAG.C, False)
        return 0
    
    def CLD(self):    
        self.setFlag(CONSTANTS.OLC6502_FLAG.D, False)
        return 0
    
    def CLI(self):    
        self.setFlag(CONSTANTS.OLC6502_FLAG.I, False)
        return 0
    
    def CLV(self):    
        self.setFlag(CONSTANTS.OLC6502_FLAG.V, False)
        return 0
    
    def CMP(self):    
        self.fetch()
        temp = self.acc - self.fetched

        self.setFlag(CONSTANTS.OLC6502_FLAG.C, self.acc >= self.fetched)
        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, (temp & 0x00FF) == 0x0000)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, temp & 0x0080)

        return 1
    
    def CPX(self):    
        self.fetch()
        temp = self.reg_x - self.fetched

        self.setFlag(CONSTANTS.OLC6502_FLAG.C, self.reg_x >= self.fetched)
        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, (temp & 0x00FF) == 0x0000)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, temp & 0x0080)

        return 0

    def CPY(self):    
        self.fetch()
        temp = self.reg_y - self.fetched

        self.setFlag(CONSTANTS.OLC6502_FLAG.C, self.reg_y >= self.fetched)
        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, (temp & 0x00FF) == 0x0000)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, temp & 0x0080)

        return 0

    def DEC(self):    
        self.fetch()
        temp = self.fetched - 1

        self.bus.write(self.addr_abs, temp & 0x00FF)

        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, (temp & 0x00FF) == 0x0000)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, temp & 0x0080)
        return 0
    
    def DEX(self):    
        self.reg_x -= 1
        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.reg_x == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.reg_x & 0x80)
        return 0
    
    def DEY(self):
        self.reg_y -= 1
        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.reg_y == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.reg_y & 0x80)
        return 0
    
    def EOR(self):    
        self.fetch()
        self.acc = self.acc ^ self.fetched	
        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.acc == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.acc & 0x80)
        return 1
    
    def INC(self):    
        self.fetch()
        temp = self.fetched + 1

        self.bus.write(self.addr_abs, temp & 0x00FF)

        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, (temp & 0x00FF) == 0x0000)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, temp & 0x0080)
        return 0
    
    def INX(self):    
        self.reg_x += 1
        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.reg_x == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.reg_x & 0x80)
        return 0
    
    def INY(self):    
        self.reg_y += 1
        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.reg_y == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.reg_y & 0x80)
        return 0
    
    def JMP(self):    
        self.pcount = self.addr_abs
        return 0
    
    def JSR(self):    
        self.pcount -= 1

        self.bus.write(0x0100 + self.stack, (self.pcount >> 8) & 0x00FF)
        self.stack -= 1

        self.bus.write(0x0100 + self.stack, self.pcount & 0x00FF)
        self.stack -= 1

        self.pcount = self.addr_abs
        return 0    

    def LDA(self):    
        self.fetch()
        self.acc = self.fetched

        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.acc == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.acc & 0x80)

        return 1

    def LDX(self):    
        self.fetch()
        self.reg_x = self.fetched

        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.reg_x == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.reg_x & 0x80)
        return 1
    
    def LDY(self):    
        self.fetch()
        self.reg_y = self.fetched

        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.reg_y == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.reg_y & 0x80)
        return 1
    
    def LSR(self):    
        self.fetch()
        self.setFlag(CONSTANTS.OLC6502_FLAG.C, self.fetched & 0x0001)

        temp = self.fetched >> 1

        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, (temp & 0x00FF) == 0x0000)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, temp & 0x0080)

        if (self.lookup[self.opcode].addrmode == self.IMP):
            self.acc = temp & 0x00FF
        else:
            self.bus.write(self.addr_abs, temp & 0x00FF)
        return 0

    def NOP(self):
        if (self.opcode == 0x1C or self.opcode == 0x3C or self.opcode == 0x5C or 
            self.opcode == 0x7C or self.opcode == 0xDC or self.opcode == 0xFC):
            return 1

        return 0

    def ORA(self):    
        self.fetch()
        self.acc = self.acc | self.fetched

        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.acc == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.acc & 0x80)

        return 1

    def PHA(self):    
        self.bus.write(0x0100 + self.stack, self.acc)
        self.stack -= 1
        return 0

    def PHP(self):    
        self.bus.write(
            0x0100 + self.stack, self.status | CONSTANTS.OLC6502_FLAG.B | CONSTANTS.OLC6502_FLAG.U)
        
        self.setFlag(CONSTANTS.OLC6502_FLAG.B, 0)
        self.setFlag(CONSTANTS.OLC6502_FLAG.U, 0)
        
        self.stack -= 1
        return 0
    
    def PLA(self):    
        self.stack += 1

        self.acc = read(0x0100 + self.stack)

        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.acc == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.acc & 0x80)
        return 0
    
    def PLP(self):    
        self.stack += 1
        self.status = self.bus.read(0x0100 + self.stack)
        self.setFlag(CONSTANTS.OLC6502_FLAG.U, 1)
        return 0
    
    def ROL(self):    
        self.fetch()
        temp = (self.fetched << 1) | self.getFlag(CONSTANTS.OLC6502_FLAG.C)

        self.setFlag(CONSTANTS.OLC6502_FLAG.C, temp & 0xFF00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, (temp & 0x00FF) == 0x0000)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, temp & 0x0080)

        if (self.lookup[self.opcode].addrmode == self.IMP):
            self.acc = temp & 0x00FF
        else:
            self.bus.write(self.addr_abs, temp & 0x00FF)
        return 0
    
    def ROR(self):    
        self.fetch()

        temp = (self.getFlag(CONSTANTS.OLC6502_FLAG.C) << 7) | (self.fetched >> 1)

        self.setFlag(CONSTANTS.OLC6502_FLAG.C, self.fetched & 0x01)
        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, (temp & 0x00FF) == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, temp & 0x0080)

        if (self.lookup[self.opcode].addrmode == self.IMP):
            self.acc = temp & 0x00FF
        else:
            self.bus.write(self.addr_abs, temp & 0x00FF)
        return 0
    
    def RTI(self):
        self.stack += 1
        self.status = self.bus.read(0x0100 + self.stack)
        self.status &= ~CONSTANTS.OLC6502_FLAG.B
        self.status &= ~CONSTANTS.OLC6502_FLAG.U

        self.stack += 1
        self.pcount = self.bus.read(0x0100 + self.stack)

        self.stack += 1
        self.pcount |= self.bus.read(0x0100 + self.stack) << 8
        return 0

    def RTS(self):
        self.stack += 1
        self.pcount = self.bus.read(0x0100 + self.stack)

        self.stack += 1
        self.pcount |= self.bus.read(0x0100 + self.stack) << 8

        self.pcount += 1
        return 0

    def SEC(self):
        self.setFlag(CONSTANTS.OLC6502_FLAG.C, True)
        return 0

    def SED(self):
        self.setFlag(CONSTANTS.OLC6502_FLAG.D, True)
        return 0

    def SEI(self):
        self.setFlag(CONSTANTS.OLC6502_FLAG.I, True)
        return 0

    def STA(self):
        self.bus.write(self.addr_abs, self.acc)
        return 0

    def STX(self):
        self.bus.write(self.addr_abs, self.reg_x)
        return 0

    def STY(self):
        self.bus.write(self.addr_abs, self.reg_y)
        return 0

    def TAX(self):
        self.reg_x = self.acc

        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.reg_x == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.reg_x & 0x80)

        return 0

    def TAY(self):
        self.reg_y = self.acc

        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.reg_y == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.reg_y & 0x80)

        return 0

    def TSX(self):
        self.reg_x = stack

        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.reg_x == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.reg_x & 0x80)

        return 0

    def TXA(self):
        self.acc = self.reg_x

        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.acc == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.acc & 0x80)

        return 0

    def TXS(self):
        self.stack = self.reg_x
        return 0

    def TYA(self):
        self.acc = self.reg_y
        
        self.setFlag(CONSTANTS.OLC6502_FLAG.Z, self.acc == 0x00)
        self.setFlag(CONSTANTS.OLC6502_FLAG.N, self.acc & 0x80)
        
        return 0

    def XXX(self):
        return 0