import cpu6502 as nes_cpu
import ppu2C02 as nes_ppu
import cartridge as nes_cartridge

class Bus:
    # Devices on bus
    cpu = nes_cpu.CPU6502()
    cpu_ram = [0x00] * 2048

    controller = [0, 0]
    controller_state = [0, 0]
    
    ppu = nes_ppu.PPU2C02()
    
    cartridge = None

    # others variables
    system_clock_counter = 0

    def __init__(self):
        self.cpu.connect_bus(self)

    def cpuRead(self, addr, is_read_only = False):
        data = 0x00

        cartridge_read = self.cartridge.cpuRead(addr)

        if cartridge_read:
            data = cartridge_read

        elif addr >= 0x0000 and addr <= 0x1FFF:
            data = self.cpu_ram[addr & 0x07FF]

        elif addr >= 0x2000 and addr <= 0x3FFF:            
            data = self.ppu.cpu_read(addr & 0x0007, is_read_only)

        elif (addr >= 0x4016 and addr <= 0x4017):
            data = (self.controller_state[addr & 0x0001] & 0x80) > 0
            self.controller_state[addr & 0x0001] <<= 1
        
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
            self.ppu.cpu_write(addr & 0x0007, data)

        elif (addr >= 0x4016 and addr <= 0x4017):
            self.controller_state[addr & 0x0001] = self.controller[addr & 0x0001]

    def insert_cartridge(self, cartridge):
        self.cartridge = cartridge
        self.ppu.connect_cartridge(cartridge)

    def reset(self):
        self.cartridge.reset()
        self.cpu.reset()
        self.ppu.reset()
        self.system_clock_counter = 0

    def clock(self):
        self.ppu.clock()

        if (self.system_clock_counter % 3 == 0):        
            self.cpu.clock()

        if self.ppu.nmi:
            self.ppu.nmi = False
            self.cpu.nmi()

        self.system_clock_counter += 1


