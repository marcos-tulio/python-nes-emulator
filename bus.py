import olc6502 as nes_cpu
import olc2C02 as nes_ppu
import cartridge as nes_cartridge

class Bus:
    # Devices on bus
    cpu = nes_cpu.Olc6502()
    cpu_ram = [0x00] * 2048
    
    ppu = nes_ppu.Olc2C02()
    
    cartridge = None

    # others variables
    system_clock_counter = 0

    def __init__(self):
        self.cpu.connectBus(self)

    def cpuRead(self, addr, isReadOnly = False):
        data = 0x00

        cartridge_read = self.cartridge.cpuRead(addr)

        if cartridge_read:
            data = cartridge_read

        elif addr >= 0x0000 and addr <= 0x1FFF:
            data = self.cpu_ram[addr & 0x07FF]

        elif addr >= 0x2000 and addr <= 0x3FFF:
            data = self.ppu.cpuRead(addr & 0x0007, isReadOnly)

        # return data in int format
        if isinstance(data, int):
            return data

        return int(data, 16)

    def cpuWrite(self, addr, data):
        if self.cartridge.cpuWrite(addr, data):
            pass

        elif addr >= 0x0000 and addr <= 0x1FFF:
            self.cpu_ram[addr & 0x07FF] = int(data)

        elif addr >= 0x2000 and addr <= 0x3FFF:
            self.ppu.cpuWrite(addr & 0x0007, data)

    def insertCartridge(self, cartridge):
        self.cartridge = cartridge
        self.ppu.connectCartridge(cartridge)

    def reset(self):
        self.cpu.reset()
        self.system_clock_counter = 0

    def clock(self):
        pass



