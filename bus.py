import olc6502 as nes_cpu

class Bus:
    # Devices on bus
    cpu = nes_cpu.Olc6502()
    ram = [0x00] * 64 * 1024 # fake ram

    def __init__(self):
        self.cpu.connectBus(self)

    def read(self, addr, isReadOnly = False):
        if addr >= 0x0000 and addr <= 0xFFFF:
            if isinstance(self.ram[addr], int):
                return self.ram[addr]

            return int(self.ram[addr], 16)

    def write(self, addr, data):
        if addr >= 0x0000 and addr <= 0xFFFF:
            self.ram[addr] = int(data)

