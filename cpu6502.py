from enum import IntEnum
from util import *

class CPU6502_FLAG(IntEnum):
    C = (1 << 0)
    Z = (1 << 1)
    I = (1 << 2)
    D = (1 << 3)
    B = (1 << 4)
    U = (1 << 5)
    V = (1 << 6)
    N = (1 << 7) 

class OP():
    def __init__(self, operate, addr_mode, cycles):
        self.operate = operate
        self.addr_mode = addr_mode
        self.cycles = cycles

class CPU6502():
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
        self.addr_rel    = 0x0000
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
        
        lo = self.read(self.addr_abs + 0) & 0XFFFF
        hi = self.read(self.addr_abs + 1) & 0XFFFF

        self.pcount = (hi << 8) | lo

        self.acc   = 0
        self.reg_x = 0
        self.reg_y = 0
        self.stack = 0xFD
        self.status = 0x00 | CPU6502_FLAG.U

        self.addr_rel = 0x0000
        self.addr_abs = 0x0000
        self.fetched = 0x00

        self.cycles = 8

    def irq(self):
        if (self.get_flag(CPU6502_FLAG.I) == 0):
            self.write(0x0100 + self.stack, (self.pcount >> 8) & 0x00FF)
            self.stack = 0xFF & (self.stack - 1)

            self.write(0x0100 + self.stack, self.pcount & 0x00FF)
            self.stack = 0xFF & (self.stack - 1)

            self.set_flag(CPU6502_FLAG.B, 0)
            self.set_flag(CPU6502_FLAG.U, 1)
            self.set_flag(CPU6502_FLAG.I, 1)

            self.write(0x0100 + self.stack, self.status)
            self.stack = 0xFF & (self.stack - 1)

            self.addr_abs = 0xFFFE

            lo = self.read(self.addr_abs + 0) & 0XFFFF
            hi = self.read(self.addr_abs + 1) & 0XFFFF

            self.pcount = (hi << 8) | lo

            self.cycles = 7

    def nmi(self):
        self.write(0x0100 + self.stack, (self.pcount >> 8) & 0x00FF)
        self.stack = 0xFF & (self.stack - 1)

        self.write(0x0100 + self.stack, self.pcount & 0x00FF)
        self.stack = 0xFF & (self.stack - 1)

        self.set_flag(CPU6502_FLAG.B, 0)
        self.set_flag(CPU6502_FLAG.U, 1)
        self.set_flag(CPU6502_FLAG.I, 1)

        self.write(0x0100 + self.stack, self.status)
        self.stack = 0xFF & (self.stack - 1)

        self.addr_abs = 0xFFFA

        lo = self.read(self.addr_abs + 0) & 0XFFFF
        hi = self.read(self.addr_abs + 1) & 0XFFFF

        self.pcount = (hi << 8) | lo

        self.cycles = 8

    def clock(self):
        if self.cycles <= 0:
            self.opcode = self.read(self.pcount)
            self.set_flag(CPU6502_FLAG.U, 1)            
            self.pcount = to_16_bits(self.pcount + 1)
            self.cycles = self.lookup[self.opcode].cycles

            additional_cycle1 = ((self.lookup[self.opcode].addr_mode)()) & 0XFF
            additional_cycle2 = ((self.lookup[self.opcode].operate)()) & 0XFF
            
            self.cycles += (additional_cycle1 & additional_cycle2)
            self.set_flag(CPU6502_FLAG.U, 1)

        self.clock_count += 1
        self.cycles -= 1

    def connect_bus(self, bus):
        self.bus = bus

    def set_flag(self, flag, value):
        if value:
            self.status |= flag
            return
        
        self.status &= ~flag

    def get_flag(self, f):
        if (self.status & f) > 0:
            return 1

        return 0

    def write(self, addr, data): self.bus.cpuWrite(addr, data)

    def read(self, addr, is_read_only = False): return self.bus.cpuRead(addr, is_read_only)

    # Addrs modes
    def IMP(self):
        self.fetched = self.acc
        return 0

    def IMM(self):
        self.addr_abs = self.pcount
        self.pcount = to_16_bits(self.pcount + 1)
        return 0

    def ZP0(self):
        self.addr_abs = self.read(self.pcount)	
        self.pcount = to_16_bits(self.pcount + 1)
        self.addr_abs &= 0x00FF
        return 0

    def ZPX(self):
        self.addr_abs = (self.read(self.pcount) + self.reg_x)
        self.pcount = to_16_bits(self.pcount + 1)
        self.addr_abs &= 0x00FF
        return 0

    def ZPY(self):
        self.addr_abs = (self.read(self.pcount) + self.reg_y)
        self.pcount = to_16_bits(self.pcount + 1)
        self.addr_abs &= 0x00FF
        return 0

    def REL(self):
        self.addr_rel = self.read(self.pcount)
        self.pcount = to_16_bits(self.pcount + 1)

        if self.addr_rel & 0x80: self.addr_rel |= 0xFF00

        return 0

    def ABS(self):
        lo = self.read(self.pcount) & 0x00FF
        self.pcount = to_16_bits(self.pcount + 1)

        hi = self.read(self.pcount) & 0x00FF
        self.pcount = to_16_bits(self.pcount + 1)

        self.addr_abs = (hi << 8) | lo

        return 0

    def ABX(self):
        lo = self.read(self.pcount)
        self.pcount = to_16_bits(self.pcount + 1)
        
        hi = self.read(self.pcount)
        self.pcount = to_16_bits(self.pcount + 1)

        self.addr_abs = (hi << 8) | lo
        self.addr_abs = to_16_bits(self.addr_abs + self.reg_x)

        if ((self.addr_abs & 0xFF00) != (hi << 8)):
            return 1

        return 0

    def ABY(self):
        lo = self.read(self.pcount)
        self.pcount = to_16_bits(self.pcount + 1)
        
        hi = self.read(self.pcount)
        self.pcount = to_16_bits(self.pcount + 1)

        self.addr_abs = (hi << 8) | lo
        self.addr_abs = to_16_bits(self.addr_abs + self.reg_y)

        if ((self.addr_abs & 0xFF00) != (hi << 8)):
            return 1

        return 0

    def IND(self):
        ptr_lo = self.read(self.pcount)
        self.pcount = to_16_bits(self.pcount + 1)

        ptr_hi = self.read(self.pcount)
        self.pcount = to_16_bits(self.pcount + 1)

        ptr = (ptr_hi << 8) | ptr_lo

        if (ptr_lo == 0x00FF): # Simulate page boundary hardware bug
            self.addr_abs = (self.read(ptr & 0xFF00) << 8) | self.read(ptr + 0)
        else:
            self.addr_abs = (self.read(ptr + 1) << 8) | self.read(ptr + 0)

        return 0

    def IZX(self):
        t = self.read(self.pcount)
        self.pcount = to_16_bits(self.pcount + 1)

        lo = self.read((t + self.reg_x) & 0x00FF)
        hi = self.read((t + self.reg_x + 1) & 0x00FF)

        self.addr_abs = (hi << 8) | lo

        return 0

    def IZY(self):
        t = self.read(self.pcount)
        self.pcount = to_16_bits(self.pcount + 1)

        lo = self.read(t & 0x00FF)
        hi = self.read((t + 1) & 0x00FF)

        self.addr_abs = (hi << 8) | lo
        self.addr_abs = to_16_bits(self.addr_abs + self.reg_y)

        if ((self.addr_abs & 0xFF00) != (hi << 8)):
            return 1

        return 0

    def fetch(self):
        if not (self.lookup[self.opcode].addr_mode == self.IMP):
            self.fetched = (self.read(self.addr_abs)) & 0xFF

        return self.fetched

    ######################################################################################
    #                                       OPCODES
    ######################################################################################

    #################################################
    # Instruction: Add with Carry In
    # Function:    A = A + M + C
    # Flags Out:   C, V, N, Z
    # Test:        Pass (IMM -, N, C)
    #################################################
    def ADC(self):
        self.fetch()
        
        acc_16     = self.acc & 0xFFFF
        fetched_16 = self.fetched & 0xFFFF

        temp    = acc_16 + fetched_16 + self.get_flag(CPU6502_FLAG.C)
        temp_8  = temp & 0x00FF
        temp_16 = temp & 0xFFFF
        
        self.set_flag(CPU6502_FLAG.C, temp > 255)
        
        self.set_flag(CPU6502_FLAG.Z, temp_8 == 0)
        
        self.set_flag(CPU6502_FLAG.V, (~(acc_16 ^ fetched_16) & (acc_16 ^ temp_16)) & 0x0080)
        
        self.set_flag(CPU6502_FLAG.N, temp & 0x80)
        
        self.acc = temp_8
        
        return 1
    
    def SBC(self):
        self.fetch()

        value = self.fetched ^ 0x00FF

        temp = self.acc + value + self.get_flag(CPU6502_FLAG.C)

        self.set_flag(CPU6502_FLAG.C, temp & 0xFF00)
        self.set_flag(CPU6502_FLAG.Z, ((temp & 0x00FF) == 0))
        self.set_flag(CPU6502_FLAG.V, (temp ^ self.acc) & (temp ^ value) & 0x0080)
        self.set_flag(CPU6502_FLAG.N, temp & 0x0080)

        self.acc = temp & 0x00FF

        return 1

    def AND(self):    
        self.fetch()
        self.acc = self.acc & self.fetched

        self.set_flag(CPU6502_FLAG.Z, self.acc == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.acc & 0x80)

        return 1
    
    def ASL(self):    
        self.fetch()
        temp = self.fetched << 1

        self.set_flag(CPU6502_FLAG.C, (temp & 0xFF00) > 0)
        self.set_flag(CPU6502_FLAG.Z, (temp & 0x00FF) == 0x00)
        self.set_flag(CPU6502_FLAG.N, temp & 0x80)

        if (self.lookup[self.opcode].addr_mode == self.IMP):
            self.acc = temp & 0x00FF
        else:
            self.write(self.addr_abs, temp & 0x00FF)

        return 0
    
    def BCC(self):    
        if (self.get_flag(CPU6502_FLAG.C) == 0):
        
            self.cycles += 1
            self.addr_abs = 0xFFFF & (self.pcount + self.addr_rel)
            
            if((self.addr_abs & 0xFF00) != (self.pcount & 0xFF00)):
                self.cycles += 1
            
            self.pcount = self.addr_abs
        
        return 0
    
    def BCS(self):    
        if (self.get_flag(CPU6502_FLAG.C) == 1):
        
            self.cycles += 1
            self.addr_abs = 0xFFFF & (self.pcount + self.addr_rel)

            if ((self.addr_abs & 0xFF00) != (self.pcount & 0xFF00)):
                self.cycles += 1

            self.pcount = self.addr_abs
        
        return 0
    
    #################################################
    # Instruction: Branch if Equal
    # Function:    if(Z == 1) pc = address
    # Flags Out:   
    # Test:        
    #################################################
    def BEQ(self): 

        if self.get_flag(CPU6502_FLAG.Z) == 1:        
            self.cycles += 1
            self.addr_abs = to_16_bits(self.pcount + self.addr_rel)

            if (self.addr_abs & 0xFF00) != (self.pcount & 0xFF00):
                self.cycles += 1

            self.pcount = self.addr_abs
        
        return 0

    def BIT(self):    
        self.fetch()
        temp = self.acc & self.fetched

        self.set_flag(CPU6502_FLAG.Z, (temp & 0x00FF) == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.fetched & (1 << 7))
        self.set_flag(CPU6502_FLAG.V, self.fetched & (1 << 6))

        return 0
    
    def BMI(self):    
        if (self.get_flag(CPU6502_FLAG.N) == 1):
        
            self.cycles += 1
            self.addr_abs = 0xFFFF & (self.pcount + self.addr_rel)

            if ((self.addr_abs & 0xFF00) != (self.pcount & 0xFF00)):
                self.cycles += 1

            self.pcount = self.addr_abs
        
        return 0

    #################################################
    # Instruction: Branch if Not Equal
    # Function:    if(Z == 0) pc = address
    # Flags Out:   
    # Test:        
    #################################################    
    def BNE(self):    
        if self.get_flag(CPU6502_FLAG.Z) == 0:        
            self.cycles += 1
            self.addr_abs = to_16_bits(self.pcount + self.addr_rel)

            if (self.addr_abs & 0xFF00) != (self.pcount & 0xFF00):
                self.cycles += 1

            self.pcount = self.addr_abs
        
        return 0
    
    def BPL(self):    
        if (self.get_flag(CPU6502_FLAG.N) == 0):        
            self.cycles += 1
            self.addr_abs = 0xFFFF & (self.pcount + self.addr_rel)

            if ((self.addr_abs & 0xFF00) != (self.pcount & 0xFF00)):
                self.cycles += 1

            self.pcount = self.addr_abs
        
        return 0
     
    #################################################
    # Instruction: Break
    # Function:    Program Sourced Interrupt 
    # Flags Out:   I, B
    # Test:        
    ################################################# 
    def BRK(self):    
        self.pcount = to_16_bits(self.pcount + 1)        
        self.set_flag(CPU6502_FLAG.I, 1)

        self.write(0x0100 + self.stack, to_8_bits(self.pcount >> 8))
        self.stack = to_8_bits(self.stack - 1)

        self.write(0x0100 + self.stack, to_8_bits(self.pcount))
        self.stack = to_8_bits(self.stack - 1)

        self.set_flag(CPU6502_FLAG.B, 1)
        self.write(0x0100 + self.stack, self.status)

        self.stack = to_8_bits(self.stack - 1)
        self.set_flag(CPU6502_FLAG.B, 0)

        self.pcount = to_16_bits(self.read(0xFFFE)) | (to_16_bits(self.read(0xFFFF)) << 8)
        return 0

    def BVC(self):
        if (self.get_flag(CPU6502_FLAG.V) == 0):
            self.cycles += 1
            self.addr_abs = 0xFFFF & (self.pcount + self.addr_rel)

            if ((self.addr_abs & 0xFF00) != (self.pcount & 0xFF00)):
                self.cycles += 1

            self.pcount = self.addr_abs
        return 0

    def BVS(self):
        if (self.get_flag(CPU6502_FLAG.V) == 1):
            self.cycles += 1
            self.addr_abs = 0xFFFF & (self.pcount + self.addr_rel)

            if ((self.addr_abs & 0xFF00) != (self.pcount & 0xFF00)):
                self.cycles += 1

            self.pcount = self.addr_abs
        return 0

    #################################################
    # Instruction: 
    # Function:    
    # Flags Out:   
    # Test:        
    #################################################
    def CLC(self):
        self.set_flag(CPU6502_FLAG.C, 0)
        return 0
    
    #################################################
    # Instruction: 
    # Function:    
    # Flags Out:   
    # Test:        
    #################################################
    def CLD(self):    
        self.set_flag(CPU6502_FLAG.D, 0)
        return 0
    
    #################################################
    # Instruction: 
    # Function:    
    # Flags Out:   
    # Test:        
    #################################################
    def CLI(self):    
        self.set_flag(CPU6502_FLAG.I, 0)
        return 0
    
    #################################################
    # Instruction: 
    # Function:    
    # Flags Out:   
    # Test:        
    #################################################
    def CLV(self):    
        self.set_flag(CPU6502_FLAG.V, 0)
        return 0

    #################################################
    # Instruction: Compare Accumulator
    # Function:    C <- A >= M      Z <- (A - M) == 0
    # Flags Out:   N, C, Z
    # Test:        
    #################################################  
    def CMP(self):    
        self.fetch()
        
        temp = to_16_bits(self.acc) - to_16_bits(self.fetched)
        temp = to_16_bits(temp)

        self.set_flag(CPU6502_FLAG.C, self.acc >= self.fetched)
        self.set_flag(CPU6502_FLAG.Z, to_8_bits(temp) == 0x0000)
        self.set_flag(CPU6502_FLAG.N, temp & 0x0080)

        return 1
    
    def CPX(self):    
        self.fetch()
        temp = self.reg_x - self.fetched

        self.set_flag(CPU6502_FLAG.C, self.reg_x >= self.fetched)
        self.set_flag(CPU6502_FLAG.Z, (temp & 0x00FF) == 0x0000)
        self.set_flag(CPU6502_FLAG.N, temp & 0x0080)

        return 0

    def CPY(self):    
        self.fetch()
        temp = self.reg_y - self.fetched

        self.set_flag(CPU6502_FLAG.C, self.reg_y >= self.fetched)
        self.set_flag(CPU6502_FLAG.Z, (temp & 0x00FF) == 0x0000)
        self.set_flag(CPU6502_FLAG.N, temp & 0x0080)

        return 0

    def DEC(self):    
        self.fetch()
        temp = self.fetched - 1

        self.write(self.addr_abs, temp & 0x00FF)

        self.set_flag(CPU6502_FLAG.Z, (temp & 0x00FF) == 0x0000)
        self.set_flag(CPU6502_FLAG.N, temp & 0x0080)
        return 0
    
    def DEX(self):    
        self.reg_x = 0xFF & (self.reg_x - 1)
        self.set_flag(CPU6502_FLAG.Z, self.reg_x == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.reg_x & 0x80)
        return 0
    
    def DEY(self):
        self.reg_y = 0xFF & (self.reg_y - 1)
        self.set_flag(CPU6502_FLAG.Z, self.reg_y == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.reg_y & 0x80)
        return 0
    
    def EOR(self):    
        self.fetch()
        self.acc = self.acc ^ self.fetched	
        self.set_flag(CPU6502_FLAG.Z, self.acc == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.acc & 0x80)
        return 1
    
    def INC(self):    
        self.fetch()
        temp = self.fetched + 1

        self.write(self.addr_abs, temp & 0x00FF)

        self.set_flag(CPU6502_FLAG.Z, (temp & 0x00FF) == 0x0000)
        self.set_flag(CPU6502_FLAG.N, temp & 0x0080)
        return 0
    
    def INX(self):    
        self.reg_x = to_8_bits(self.reg_x + 1)
        self.set_flag(CPU6502_FLAG.Z, self.reg_x == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.reg_x & 0x80)
        return 0

    #################################################
    # Instruction: Increment Y Register
    # Function:    Y = Y + 1
    # Flags Out:    N, Z
    # Test:
    #################################################     
    def INY(self):    
        self.reg_y = to_8_bits(self.reg_y + 1)
        self.set_flag(CPU6502_FLAG.Z, self.reg_y == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.reg_y & 0x80)
        return 0
    
    def JMP(self):    
        self.pcount = self.addr_abs
        return 0

    #################################################
    # Instruction: Jump To Sub-Routine
    # Function:    Push current pc to stack, pc = address
    # Flags Out:
    # Test:
    #################################################    
    def JSR(self):    
        self.pcount = to_16_bits(self.pcount - 1)

        self.write(0x0100 + self.stack, to_8_bits(self.pcount >> 8))
        self.stack = to_8_bits(self.stack - 1)

        self.write(0x0100 + self.stack, to_8_bits(self.pcount))
        self.stack = to_8_bits(self.stack - 1)

        self.pcount = self.addr_abs
        return 0    

    #################################################
    # Instruction: Load The Accumulator
    # Function:    A = M
    # Flags Out:   N, Z
    # Test:        Pass (IMM)
    #################################################
    def LDA(self):    
        self.fetch()
        self.acc = self.fetched

        self.set_flag(CPU6502_FLAG.Z, self.acc == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.acc & 0x80)

        return 1

    #################################################
    # Instruction: Load The X Register
    # Function:    X = M
    # Flags Out:   N, Z
    # Test:        Pass (IMM)
    #################################################
    def LDX(self):    
        self.fetch()
        self.reg_x = self.fetched

        self.set_flag(CPU6502_FLAG.Z, self.reg_x == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.reg_x & 0x80)
        return 1
    
    #################################################
    # Instruction: Load The Y Register
    # Function:    Y = M
    # Flags Out:   N, Z
    # Test:        Pass (IMM)
    #################################################
    def LDY(self):    
        self.fetch()
        self.reg_y = self.fetched

        self.set_flag(CPU6502_FLAG.Z, self.reg_y == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.reg_y & 0x80)
        return 1
    
    def LSR(self):    
        self.fetch()
        self.set_flag(CPU6502_FLAG.C, self.fetched & 0x0001)

        temp = self.fetched >> 1

        self.set_flag(CPU6502_FLAG.Z, (temp & 0x00FF) == 0x0000)
        self.set_flag(CPU6502_FLAG.N, temp & 0x0080)

        if (self.lookup[self.opcode].addr_mode == self.IMP):
            self.acc = temp & 0x00FF
        else:
            self.write(self.addr_abs, temp & 0x00FF)
        return 0

    #################################################
    # Instruction: Not operate
    # Function:    
    # Flags Out:   
    # Test:        
    #################################################
    def NOP(self):
        if (self.opcode == 0x1C or self.opcode == 0x3C or self.opcode == 0x5C or 
            self.opcode == 0x7C or self.opcode == 0xDC or self.opcode == 0xFC):
            return 1

        return 0

    def ORA(self):    
        self.fetch()
        self.acc = self.acc | self.fetched

        self.set_flag(CPU6502_FLAG.Z, self.acc == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.acc & 0x80)

        return 1

    def PHA(self):    
        self.write(0x0100 + self.stack, self.acc)
        self.stack = 0xFF & (self.stack - 1)
        return 0

    def PHP(self):    
        self.write(
            0x0100 + self.stack, self.status | CPU6502_FLAG.B | CPU6502_FLAG.U)
        
        self.set_flag(CPU6502_FLAG.B, 0)
        self.set_flag(CPU6502_FLAG.U, 0)
        
        self.stack = 0xFF & (self.stack - 1)
        return 0
    
    def PLA(self):    
        self.stack = to_8_bits(self.stack + 1)

        self.acc = self.read(0x0100 + self.stack)

        self.set_flag(CPU6502_FLAG.Z, self.acc == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.acc & 0x80)
        return 0
    
    def PLP(self):    
        self.stack = to_8_bits(self.stack + 1)
        self.status = self.read(0x0100 + self.stack)
        self.set_flag(CPU6502_FLAG.U, 1)
        return 0
    
    def ROL(self):    
        self.fetch()
        temp = (self.fetched << 1) | self.get_flag(CPU6502_FLAG.C)

        self.set_flag(CPU6502_FLAG.C, temp & 0xFF00)
        self.set_flag(CPU6502_FLAG.Z, (temp & 0x00FF) == 0x0000)
        self.set_flag(CPU6502_FLAG.N, temp & 0x0080)

        if (self.lookup[self.opcode].addr_mode == self.IMP):
            self.acc = temp & 0x00FF
        else:
            self.write(self.addr_abs, temp & 0x00FF)
        return 0
    
    def ROR(self):    
        self.fetch()

        temp = (self.get_flag(CPU6502_FLAG.C) << 7) | (self.fetched >> 1)

        self.set_flag(CPU6502_FLAG.C, self.fetched & 0x01)
        self.set_flag(CPU6502_FLAG.Z, (temp & 0x00FF) == 0x00)
        self.set_flag(CPU6502_FLAG.N, temp & 0x0080)

        if (self.lookup[self.opcode].addr_mode == self.IMP):
            self.acc = temp & 0x00FF
        else:
            self.write(self.addr_abs, temp & 0x00FF)
        return 0
    
    def RTI(self):
        self.stack = to_8_bits(self.stack + 1)
        self.status = self.read(0x0100 + self.stack)
        self.status &= ~CPU6502_FLAG.B
        self.status &= ~CPU6502_FLAG.U

        self.stack = to_8_bits(self.stack + 1)
        self.pcount = self.read(0x0100 + self.stack)

        self.stack = to_8_bits(self.stack + 1)
        self.pcount |= self.read(0x0100 + self.stack) << 8
        return 0

    def RTS(self):
        self.stack = to_8_bits(self.stack + 1)
        self.pcount = self.read(0x0100 + self.stack)

        self.stack = to_8_bits(self.stack + 1)
        self.pcount |= self.read(0x0100 + self.stack) << 8

        self.pcount = to_16_bits(self.pcount + 1)
        return 0

    def SEC(self):
        self.set_flag(CPU6502_FLAG.C, 1)
        return 0

    def SED(self):
        self.set_flag(CPU6502_FLAG.D, 1)
        return 0

    # Pass (IMP)
    def SEI(self):
        self.set_flag(CPU6502_FLAG.I, 1)
        return 0

    #################################################
    # Instruction: Store Accumulator at Address
    # Function:    M = A
    # Flags Out:   
    # Test:        Pass (ABS)
    #################################################
    def STA(self): 
        self.write(self.addr_abs, self.acc)
        return 0

    #################################################
    # Instruction: Store X Register at Address
    # Function:    M = X
    # Flags Out:   
    # Test:        Pass (ABS)
    #################################################
    def STX(self):
        self.write(self.addr_abs, self.reg_x)
        return 0

    #################################################
    # Instruction: Store Y Register at Address
    # Function:    M = Y
    # Flags Out:   
    # Test:        Pass (ABS)
    #################################################
    def STY(self):
        self.write(self.addr_abs, self.reg_y)
        return 0

    #################################################
    # Instruction: Transfer Accumulator to X Register
    # Function:    X = A
    # Flags Out:   N, Z
    # Test:        Pass (IMP)
    #################################################
    def TAX(self):
        self.reg_x = self.acc

        self.set_flag(CPU6502_FLAG.Z, self.reg_x == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.reg_x & 0x80)

        return 0

    #################################################
    # Instruction: Transfer Accumulator to Y Register
    # Function:    Y = A
    # Flags Out:   N, Z
    # Test:        Pass (IMP)
    #################################################
    def TAY(self):
        self.reg_y = self.acc

        self.set_flag(CPU6502_FLAG.Z, self.reg_y == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.reg_y & 0x80)

        return 0

    #################################################
    # Instruction: 
    # Function:    
    # Flags Out:   
    # Test:        
    #################################################
    def TSX(self):
        self.reg_x = self.stack

        self.set_flag(CPU6502_FLAG.Z, self.reg_x == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.reg_x & 0x80)

        return 0

    #################################################
    # Instruction: 
    # Function:    
    # Flags Out:   
    # Test:        
    #################################################
    def TXS(self):
        self.stack = self.reg_x
        return 0

    #################################################
    # Instruction: Transfer X Register to Accumulator
    # Function:    A = X
    # Flags Out:   N, Z
    # Test:        Pass (IMP)
    #################################################
    def TXA(self):
        self.acc = self.reg_x

        self.set_flag(CPU6502_FLAG.Z, self.acc == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.acc & 0x80)

        return 0

    #################################################
    # Instruction: Transfer Y Register to Accumulator
    # Function:    A = Y
    # Flags Out:   N, Z
    # Test:        Pass (IMP)
    #################################################
    def TYA(self):
        self.acc = self.reg_y
        
        self.set_flag(CPU6502_FLAG.Z, self.acc == 0x00)
        self.set_flag(CPU6502_FLAG.N, self.acc & 0x80)
        
        return 0

    #################################################
    # Instruction: This function captures illegal opcodes
    # Function:    
    # Flags Out:   
    # Test:        
    #################################################
    def XXX(self): return 0

    ###########################################
    # Helpers
    #################################
    def complete(self):
	    return self.cycles == 0
    
    used_opcodes = {}

    def disassemble(self, nStart, nStop):
        addr = nStart
        value = 0x00
        lo = 0x00
        hi = 0x00

        map_lines = {}
        line_addr = 0

        while (addr <= nStop):
            line_addr = addr

            sInst = "${:04x}: ".format(addr)
            
            opcode = self.read(addr, True)
            addr += 1
            
            sInst += str(self.lookup[opcode].operate.__name__) + " "

            if (self.lookup[opcode].addr_mode == self.IMP):
                sInst += " (IMP)"

            elif (self.lookup[opcode].addr_mode == self.IMM):
                value = self.read(addr, True) 
                addr += 1
                sInst += "#${:02x} (IMM)".format(value)

            elif (self.lookup[opcode].addr_mode == self.ZP0):
                lo = self.read(addr, True) 
                addr += 1
                hi = 0x00												
                sInst += "${:02x} (ZP0)".format(lo)

            elif (self.lookup[opcode].addr_mode == self.ZPX):
                lo = self.read(addr, True) 
                addr += 1
                hi = 0x00	
                sInst += "${:02x}, X (ZPX)".format(lo)

            elif (self.lookup[opcode].addr_mode == self.ZPY):
                lo = self.read(addr, True) 
                addr += 1
                hi = 0x00
                sInst += "${:02x}, Y (ZPY)".format(lo)

            elif (self.lookup[opcode].addr_mode == self.IZX):
                lo = self.read(addr, True) 
                addr += 1
                hi = 0x00			
                sInst += "${:02x}, X (IZX)".format(lo)

            elif (self.lookup[opcode].addr_mode == self.IZY):
                lo = self.read(addr, True) 
                addr += 1
                hi = 0x00
                sInst += "${:02x}, Y (IZY)".format(lo)

            elif (self.lookup[opcode].addr_mode == self.ABS):
                lo = self.read(addr, True) 
                addr += 1

                hi = self.read(addr, True) 
                addr += 1
                sInst += "${:04x} (ABS)".format((hi << 8) | lo)

            elif (self.lookup[opcode].addr_mode == self.ABX):
                lo = self.read(addr, True) 
                addr += 1

                hi = self.read(addr, True) 
                addr += 1
                sInst += "${:04x}, X (ABX)".format((hi << 8) | lo)

            elif (self.lookup[opcode].addr_mode == self.ABY):
                lo = self.read(addr, True) 
                addr += 1

                hi = self.read(addr, True) 
                addr += 1
                sInst += "${:04x}, Y (ABY)".format((hi << 8) | lo)

            elif (self.lookup[opcode].addr_mode == self.IND):
                lo = self.read(addr, True) 
                addr += 1

                hi = self.read(addr, True) 
                addr += 1
                sInst += "(${:04x}) (IND)".format((hi << 8) | lo)

            elif (self.lookup[opcode].addr_mode == self.REL):
                value = self.read(addr, True) 
                addr += 1
                sInst += "${:02x} [${:04x}] (REL)".format(value, (addr + value))

            map_lines[line_addr] = sInst

            value = 0
            try:
                if self.used_opcodes[sInst[7:10]]:
                    value = self.used_opcodes[sInst[7:10]]
            except: pass

            self.used_opcodes[sInst[7:10]] = value + 1

        return map_lines