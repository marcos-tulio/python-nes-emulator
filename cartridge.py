from enum import IntEnum
import mapper_000

class INesHeader():
    def __init__(self):
        self.name = ""
        self.prg_rom_chunks = 0
        self.chr_rom_chunks = 0
        self.mapper1 = 0
        self.mapper2 = 0
        self.prg_ram_size = 0
        self.tv_system1 = 0
        self.tv_system2 = 0
        self.unused = ""

class MIRROR(IntEnum):
    HORIZONTAL   = 0
    VERTICAL     = 1
    ONESCREEN_LO = 2
    ONESCREEN_HI = 3

class Cartridge():
    prg_memory = None
    chr_memory = None

    mapper_id = 0
    prg_banks = 0
    chr_banks = 0

    is_rom_valid = False
    mirror = MIRROR.HORIZONTAL

    mapper = None

    def __init__(self, file_path):
        file = open(file_path, "rb")

        # read 16 first bytes
        self.header = INesHeader()
        self.header.name            = str(file.read(4))
        self.header.prg_rom_chunks  = int.from_bytes(file.read(1), 'big')
        self.header.chr_rom_chunks  = int.from_bytes(file.read(1), 'big')
        self.header.mapper1         = int.from_bytes(file.read(1), 'big')
        self.header.mapper2         = int.from_bytes(file.read(1), 'big')
        self.header.prg_ram_size    = int.from_bytes(file.read(1), 'big')
        self.header.tv_system1      = int.from_bytes(file.read(1), 'big')
        self.header.tv_system1      = int.from_bytes(file.read(1), 'big')
        self.header.unused          = str(file.read(5))

        # skip trainer
        if self.header.mapper1 & 0x04:
            file.seek(512)

        # Mapper ID
        self.mapper_id = ((self.header.mapper2 >> 4) << 4) | (self.header.mapper1 >> 4)
        
        # Mirror mode
        if self.header.mapper1 & 0x01: self.mirror = MIRROR.VERTICAL
        else: self.mirror = MIRROR.HORIZONTAL

		# "Discover" File Format
        file_type = 1

        if file_type == 0:
            pass

        elif file_type == 1:
            self.prg_banks = self.header.prg_rom_chunks
            self.prg_memory = list(file.read(self.prg_banks * 16384))

            self.chr_banks = self.header.chr_rom_chunks
            self.chr_memory = list(file.read(self.chr_banks * 8192))

        elif file_type == 2:
            pass
        
        # load mapper
        if self.mapper_id == 0:
            self.mapper = mapper_000.Mapper000(self.prg_banks, self.chr_banks)

        self.is_rom_valid = True
        file.close()

        # Debug
        print ("Mapper_ID: ", self.mapper_id)
        print ("PRG_rom_chunks: ", self.header.prg_rom_chunks)
        print ("CHR_rom_chunks: ", self.header.chr_rom_chunks)
        print ("Mapper_1: ", self.header.mapper1)
        print ("Mapper_2: ", self.header.mapper2)
        print ("PRG_ram_size: ", self.header.prg_ram_size)
        print ("TV_system1: ", self.header.tv_system1)
        print ("TV_system2: ", self.header.tv_system2)
        print ()

    def cpuRead(self, addr):        
        mapped_addr = self.mapper.cpuMapRead(addr)

        if not (mapped_addr == None):
            return self.prg_memory[mapped_addr]

        return None

    def cpuWrite(self, addr, data):
        mapped_addr = self.mapper.cpuMapWrite(addr)

        if mapped_addr:
            self.prg_memory[mapped_addr] = data
            return True

        return False

    def ppuRead(self, addr, isReadOnly = False):
        mapped_addr = self.mapper.ppuMapRead(addr)
        
        if not (mapped_addr == None):     
            return self.chr_memory[mapped_addr]

        return None

    def ppuWrite(self, addr, data):
        mapped_addr = self.mapper.ppuMapWrite(addr)

        if not (mapped_addr == None):
            self.chr_memory[mapped_addr] = data
            return True

        return False

    def reset(self):
        if self.mapper: self.mapper.reset()