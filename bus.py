import olc6502 as nes_cpu

class Bus:
    # Devices on bus
    cpu = nes_cpu.Olc6502()
    ram = [0x00] * 64 * 1024 # fake ram

    def __init__(self):
        self.cpu.connectBus(self)

    def read(self, addr, isReadOnly = False):
        '''
        Read a byte from bus.
            addr = 16 bits, isReadOnly = 1 bit
        
        return 8 bits.
        '''

        if addr >= 0x0000 and addr <= 0xFFFF:
            return self.ram[addr]

            print("read in addr", addr)

    def write(self, addr, data):
        '''
        Write a byte in bus.
            addr = 16 bits, data = 8 bits
        '''

        if addr >= 0x0000 and addr <= 0xFFFF:
            self.ram[addr] = data

            print("write {} in addr {}".format(data, addr))

