import mapper as m

class Mapper000(m.Mapper):
    def cpuMapRead(self, addr):
        if addr >= 0x8000 and addr <= 0xFFFF:
            value = 0x7FFF

            if not self.prg_banks > 1:
                value = 0x3FFF

            return addr & value

        return None

    def cpuMapWrite(self, addr):
        if addr >= 0x8000 and addr <= 0xFFFF:
            value = 0x7FFF

            if not self.prg_banks > 1:
                value = 0x3FFF

            return addr & value

        return None

    def ppuMapRead(self, addr):
        if addr >= 0x0000 and addr <= 0x1FFF:
            return addr

        return None

    def ppuMapWrite(self, addr):
        if addr >= 0x0000 and addr <= 0x1FFF:
            if self.chr_banks == 0:
                return addr

        return None

    def reset(self): pass
        
