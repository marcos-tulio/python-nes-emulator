from util import to_16_bits, to_8_bits
import graphics as g
import cartridge as c
import numpy as np

class BitRegister():
    reg = 0x00

    def set_reg(self, bit, value): self.reg = (self.reg | bit) if value else (self.reg & ~bit)

    def get_reg(self, bit): return 0x01 if self.reg & bit else 0x00

class Status(BitRegister):
    # 5 bits -> unused
    # 1 bit  -> sprite_overflow
    # 1 bit  -> sprite_zero_hit
    # 1 bit  -> vertical_blank

    def set_sprite_overflow(self, value): self.set_reg(0x20, value)
    def set_sprite_zero_hit(self, value): self.set_reg(0x40, value)    
    def set_vertical_blank (self, value): self.set_reg(0x80, value)

    def get_sprite_overflow(self): return self.get_reg(0x20)
    def get_sprite_zero_hit(self): return self.get_reg(0x40)
    def get_vertical_blank (self): return self.get_reg(0x80)

class Mask(BitRegister):
    # 1 bit -> grayscale
    # 1 bit -> render_background_left
    # 1 bit -> render_sprites_left
    # 1 bit -> render_background
    # 1 bit -> render_sprites
    # 1 bit -> enhance_red
    # 1 bit -> enhance_green
    # 1 bit -> enhance_blue

    def set_grayscale              (self, value): self.set_reg(0x01, value)
    def set_render_background_left (self, value): self.set_reg(0x02, value)
    def set_render_sprites_left    (self, value): self.set_reg(0x04, value)
    def set_render_background      (self, value): self.set_reg(0x08, value)
    def set_render_sprites         (self, value): self.set_reg(0x10, value)
    def set_enhance_red            (self, value): self.set_reg(0x20, value)
    def set_enhance_green          (self, value): self.set_reg(0x40, value)
    def set_enhance_blue           (self, value): self.set_reg(0x80, value)

    def get_grayscale              (self): return self.get_reg(0x01)
    def get_render_background_left (self): return self.get_reg(0x02)
    def get_render_sprites_left    (self): return self.get_reg(0x04)
    def get_render_background      (self): return self.get_reg(0x08)
    def get_render_sprites         (self): return self.get_reg(0x10)
    def get_enhance_red            (self): return self.get_reg(0x20)
    def get_enhance_green          (self): return self.get_reg(0x40)
    def get_enhance_blue           (self): return self.get_reg(0x80)

class Control(BitRegister):
    # 1 bit -> nametable_x
    # 1 bit -> nametable_y
    # 1 bit -> increment_mode
    # 1 bit -> pattern_sprite
    # 1 bit -> pattern_background
    # 1 bit -> sprite_size
    # 1 bit -> slave_mode
    # 1 bit -> enable_nmi

    def set_nametable_x       (self, value): self.set_reg(0x01, value)
    def set_nametable_y       (self, value): self.set_reg(0x02, value)
    def set_increment_mode    (self, value): self.set_reg(0x04, value)
    def set_pattern_sprite    (self, value): self.set_reg(0x08, value)
    def set_pattern_background(self, value): self.set_reg(0x10, value)
    def set_sprite_size       (self, value): self.set_reg(0x20, value)
    def set_slave_mode        (self, value): self.set_reg(0x40, value)
    def set_enable_nmi        (self, value): self.set_reg(0x80, value)

    def get_nametable_x       (self): return self.get_reg(0x01)
    def get_nametable_y       (self): return self.get_reg(0x02)
    def get_increment_mode    (self): return self.get_reg(0x04)
    def get_pattern_sprite    (self): return self.get_reg(0x08)
    def get_pattern_background(self): return self.get_reg(0x10)
    def get_sprite_size       (self): return self.get_reg(0x20)
    def get_slave_mode        (self): return self.get_reg(0x40)
    def get_enable_nmi        (self): return self.get_reg(0x80)

class LoopyRegister(BitRegister):
    # 5 bits -> coarse_x = 5
    # 5 bits -> coarse_y = 5
    # 1 bit  -> nametable_x = 1
    # 1 bit  -> nametable_y = 1
    # 3 bits -> fine_y = 3
    # 1 bit  -> unused = 1

    def set_coarse_x(self, value):
        self.reg &= ~0x001F
        self.reg |= value & 0x001F

    def set_coarse_y(self, value):
        self.reg &= ~0x03E0
        self.reg |= (value & 0x001F) << 5

    def set_nametable_x(self, value): self.set_reg(0x0400, value)

    def set_nametable_y(self, value): self.set_reg(0x0800, value)

    def set_fine_y(self, value): 
        self.reg &= ~0x7000
        self.reg |= (value & 0x0007) << 12

    def get_coarse_x   (self): return self.reg & 0x001F

    def get_coarse_y   (self): return (self.reg & 0x03E0) >> 5

    def get_nametable_x(self): return self.get_reg(0x0400)

    def get_nametable_y(self): return self.get_reg(0x0800)

    def get_fine_y     (self): return (self.reg & 0x7000) >> 12

class PPU2C02():
    enable_log = False

    mask = Mask()
    status = Status()
    control = Control()

    vram_addr = LoopyRegister()
    tram_addr = LoopyRegister()
    fine_x    = 0x00

    tbl_name    = [[0x00]* 1024] * 2
    tbl_palette = [ 0xFF]* 32
    tbl_pattern = [[0x00]* 4096] * 2

    cartridge   = None
    
    address_latch   = 0x00
    ppu_data_buffer = 0x00
    #ppu_address     = 0x0000

	# Background rendering
    bg_next_tile_id     = 0x00
    bg_next_tile_attrib = 0x00
    bg_next_tile_lsb    = 0x00
    bg_next_tile_msb    = 0x00
    bg_shifter_pattern_lo = 0x0000
    bg_shifter_pattern_hi = 0x0000
    bg_shifter_attrib_lo  = 0x0000
    bg_shifter_attrib_hi  = 0x0000

    nmi = False

    scanline = 0
    cycle    = 0
    frame_complete = False

    def __init__(self):
        # Initial random palette
        for i in range(len(self.tbl_palette)):
            self.tbl_palette[i] = int(np.random.rand() * 100) & 0xFF

        # Sprites
        self.spr_screen      =   g.Sprite(256, 240)
        self.spr_name_tbl    = [ g.Sprite(256, 240), g.Sprite(256, 240)]
        self.spr_pattern_tbl = [ g.Sprite(128, 128), g.Sprite(128, 128)]

        # Pixels
        self.pal_screen = [
            g.Pixel(84, 84, 84)   , g.Pixel(0, 30, 116)   , g.Pixel(8, 16, 144),
            g.Pixel(48, 0, 136)   , g.Pixel(68, 0, 100)   , g.Pixel(92, 0, 48),
            g.Pixel(84, 4, 0)     , g.Pixel(60, 24, 0)    , g.Pixel(32, 42, 0),
            g.Pixel(8, 58, 0)     , g.Pixel(0, 64, 0)     , g.Pixel(0, 60, 0),
            g.Pixel(0, 50, 60)    , g.Pixel(0, 0, 0)      , g.Pixel(0, 0, 0),
            g.Pixel(0, 0, 0)      , g.Pixel(152, 150, 152), g.Pixel(8, 76, 196),
            g.Pixel(48, 50, 236)  , g.Pixel(92, 30, 228)  , g.Pixel(136, 20, 176),
            g.Pixel(160, 20, 100) , g.Pixel(152, 34, 32)  , g.Pixel(120, 60, 0),
            g.Pixel(84, 90, 0)    , g.Pixel(40, 114, 0)   , g.Pixel(8, 124, 0),
            g.Pixel(0, 118, 40)   , g.Pixel(0, 102, 120)  , g.Pixel(0, 0, 0),
            g.Pixel(0, 0, 0)      , g.Pixel(0, 0, 0)      , g.Pixel(236, 238, 236),
            g.Pixel(76, 154, 236) , g.Pixel(120, 124, 236), g.Pixel(176, 98, 236),
            g.Pixel(228, 84, 236) , g.Pixel(236, 88, 180) , g.Pixel(236, 106, 100),
            g.Pixel(212, 136, 32) , g.Pixel(160, 170, 0)  , g.Pixel(116, 196, 0),
            g.Pixel(76, 208, 32)  , g.Pixel(56, 204, 108) , g.Pixel(56, 180, 204),
            g.Pixel(60, 60, 60)   , g.Pixel(0, 0, 0)      , g.Pixel(0, 0, 0),
            g.Pixel(236, 238, 236), g.Pixel(168, 204, 236), g.Pixel(188, 188, 236),
            g.Pixel(212, 178, 236), g.Pixel(236, 174, 236), g.Pixel(236, 174, 212),
            g.Pixel(236, 180, 176), g.Pixel(228, 196, 144), g.Pixel(204, 210, 120),
            g.Pixel(180, 222, 120), g.Pixel(168, 226, 144), g.Pixel(152, 226, 180),
            g.Pixel(160, 214, 228), g.Pixel(160, 162, 160), g.Pixel(0, 0, 0),
            g.Pixel(0, 0, 0)
        ]

    def cpu_read(self, addr, is_read_only = False):
        if addr > 0xFFFF: print("maior que 16 bits") 
        

        data = 0x00

        
        if is_read_only:
            if   addr == 0x0000: data = self.control.reg
            elif addr == 0x0001: data = self.mask.reg
            elif addr == 0x0002: data = self.status.reg
            elif addr == 0x0003: pass
            elif addr == 0x0004: pass
            elif addr == 0x0005: pass
            elif addr == 0x0006: pass
            elif addr == 0x0007: pass

        else:        
            if   addr == 0x0000: pass
            elif addr == 0x0001: pass
            elif addr == 0x0002:
                #self.status.set_vertical_blank(1)

                data = (self.status.reg & 0xE0) | (self.ppu_data_buffer & 0x1F)

                self.status.set_vertical_blank(0)

                self.address_latch = 0
            elif addr == 0x0003: pass
            elif addr == 0x0004: pass
            elif addr == 0x0005: pass
            elif addr == 0x0006: pass
            elif addr == 0x0007:
                data = self.ppu_data_buffer

                self.ppu_data_buffer = self.ppu_read(self.vram_addr.reg)

                if (self.vram_addr.reg >= 0x3F00): data = self.ppu_data_buffer

                self.vram_addr.reg = to_16_bits(
                    self.vram_addr.reg + (32 if self.control.get_increment_mode() else 1))

        if data > 0xFF: print("maior que 8 bits") 

        return to_8_bits(data)

    def cpu_write(self, addr, data):
        if addr > 0xFFFF: print("maior que 16 bits") 
        if data > 0xFF: print("maior que 8 bits") 

        if addr == 0x0000:      # control
            self.control.reg = data
            self.tram_addr.set_nametable_x(self.control.get_nametable_x()) 
            self.tram_addr.set_nametable_y(self.control.get_nametable_y())

        elif addr == 0x0001: self.mask.reg = data # mask

        elif addr == 0x0002:    # status
            pass

        elif addr == 0x0003:    # OAM Address
            pass

        elif addr == 0x0004:    # OAM Data
            pass

        elif addr == 0x0005:    # Scroll
            if (self.address_latch == 0):
                self.fine_x = data & 0x07
                self.tram_addr.set_coarse_x(data >> 3)
                self.address_latch = 1

            else:
                self.tram_addr.set_fine_y(data & 0x07)
                self.tram_addr.set_coarse_y(data >> 3)
                self.address_latch = 0
            
        elif addr == 0x0006:    # PPU Address
            if self.address_latch == 0:
                self.tram_addr.reg = to_16_bits((data & 0x3F) << 8) | (self.tram_addr.reg & 0x00FF)
                self.address_latch = 1

            else:
                self.tram_addr.reg = to_16_bits((self.tram_addr.reg & 0xFF00) | data)
                self.vram_addr.reg = self.tram_addr.reg
                self.address_latch = 0

        elif addr == 0x0007:    # PPU Data
            self.ppu_write(self.vram_addr.reg, data)
            self.vram_addr.reg = to_16_bits(
                self.vram_addr.reg + (32 if self.control.get_increment_mode() else 1))

    def ppu_read(self, addr, is_read_only = False):
        if addr > 0xFFFF: print("maior que 16 bits") 

        data = 0x00
        addr &= 0x3FFF

        ret = self.cartridge.ppuRead(addr, data)

        if not(ret == None): data = to_8_bits(ret)

        elif (addr >= 0x0000 and addr <= 0x1FFF):
            data = self.tbl_pattern[(addr & 0x1000) >> 12][addr & 0x0FFF]

        elif (addr >= 0x2000 and addr <= 0x3EFF):
            addr &= 0x0FFF

            if self.cartridge.mirror == c.MIRROR.VERTICAL:
                if (addr >= 0x0000 and addr <= 0x03FF): data = self.tbl_name[0][addr & 0x03FF]
                if (addr >= 0x0400 and addr <= 0x07FF): data = self.tbl_name[1][addr & 0x03FF]
                if (addr >= 0x0800 and addr <= 0x0BFF): data = self.tbl_name[0][addr & 0x03FF]
                if (addr >= 0x0C00 and addr <= 0x0FFF): data = self.tbl_name[1][addr & 0x03FF]

            elif self.cartridge.mirror == c.MIRROR.HORIZONTAL:
                if (addr >= 0x0000 and addr <= 0x03FF): data = self.tbl_name[0][addr & 0x03FF]
                if (addr >= 0x0400 and addr <= 0x07FF): data = self.tbl_name[0][addr & 0x03FF]
                if (addr >= 0x0800 and addr <= 0x0BFF): data = self.tbl_name[1][addr & 0x03FF]
                if (addr >= 0x0C00 and addr <= 0x0FFF): data = self.tbl_name[1][addr & 0x03FF]

        elif (addr >= 0x3F00 and addr <= 0x3FFF):
            addr &= 0x001F

            if (addr == 0x0010): addr = 0x0000
            if (addr == 0x0014): addr = 0x0004
            if (addr == 0x0018): addr = 0x0008
            if (addr == 0x001C): addr = 0x000C

            #data = self.tbl_palette[addr]
            data = self.tbl_palette[addr] & (0x30 if self.mask.get_grayscale() else 0x3F)

        if data > 0xFF: print("maior que 8 bits") 

        return data

    def ppu_write(self, addr, data):
        if addr > 0xFFFF: print("maior que 16 bits") 
        if data > 0xFF: print("maior que 8 bits") 

        data = to_8_bits(data)
        addr &= 0x3FFF

        if self.cartridge.ppuWrite(addr, data):
            pass

        elif (addr >= 0x0000 and addr <= 0x1FFF):
            self.tbl_pattern[(addr & 0x1000) >> 12][addr & 0x0FFF] = data

        elif (addr >= 0x2000 and addr <= 0x3EFF):
            addr &= 0x0FFF

            if self.cartridge.mirror == c.MIRROR.VERTICAL:
                if (addr >= 0x0000 and addr <= 0x03FF): self.tbl_name[0][addr & 0x03FF] = data
                if (addr >= 0x0400 and addr <= 0x07FF): self.tbl_name[1][addr & 0x03FF] = data
                if (addr >= 0x0800 and addr <= 0x0BFF): self.tbl_name[0][addr & 0x03FF] = data
                if (addr >= 0x0C00 and addr <= 0x0FFF): self.tbl_name[1][addr & 0x03FF] = data

            elif self.cartridge.mirror == c.MIRROR.HORIZONTAL:
                if (addr >= 0x0000 and addr <= 0x03FF): self.tbl_name[0][addr & 0x03FF] = data
                if (addr >= 0x0400 and addr <= 0x07FF): self.tbl_name[0][addr & 0x03FF] = data
                if (addr >= 0x0800 and addr <= 0x0BFF): self.tbl_name[1][addr & 0x03FF] = data
                if (addr >= 0x0C00 and addr <= 0x0FFF): self.tbl_name[1][addr & 0x03FF] = data

        elif (addr >= 0x3F00 and addr <= 0x3FFF):
            addr &= 0x001F

            if (addr == 0x0010): addr = 0x0000
            if (addr == 0x0014): addr = 0x0004
            if (addr == 0x0018): addr = 0x0008
            if (addr == 0x001C): addr = 0x000C

            self.tbl_palette[addr] = data

    def get_pattern_table(self, i, palette):
        for nTileY in range(16):
            for nTileX in range(16):
                nOffset = to_16_bits(nTileY * 256 + nTileX * 16)

                for row in range(8):
                    tile_lsb = to_8_bits(self.ppu_read(i * 0x1000 + nOffset + row + 0x0000))
                    tile_msb = to_8_bits(self.ppu_read(i * 0x1000 + nOffset + row + 0x0008))

                    for col in range(8):
                        pixel = to_8_bits((tile_lsb & 0x01) + (tile_msb & 0x01))

                        tile_lsb >>= 1
                        tile_msb >>= 1

                        self.spr_pattern_tbl[i].set_pixel(
                            nTileX * 8 + (7 - col),
                            nTileY * 8 + row,
                            self.get_colour_from_palette_ram(palette, pixel)
                        )

        return self.spr_pattern_tbl[i]

    def get_colour_from_palette_ram(self, palette, pixel):

        value = to_8_bits(self.ppu_read(0x3F00 + (palette << 2) + pixel))

        return self.pal_screen[value & 0x3F]

    def connect_cartridge(self, cartridge): self.cartridge = cartridge

    def reset(self):
        self.fine_x = 0x00
        self.address_latch = 0x00
        self.ppu_data_buffer = 0x00
        self.scanline = 0
        self.cycle = 0

        self.bg_next_tile_id = 0x00
        self.bg_next_tile_attrib = 0x00
        self.bg_next_tile_lsb = 0x00
        self.bg_next_tile_msb = 0x00

        self.bg_shifter_pattern_lo = 0x0000
        self.bg_shifter_pattern_hi = 0x0000
        self.bg_shifter_attrib_lo = 0x0000
        self.bg_shifter_attrib_hi = 0x0000

        self.status.reg = 0x00
        self.mask.reg = 0x00
        self.control.reg = 0x00
        self.vram_addr.reg = 0x0000
        self.tram_addr.reg = 0x0000

    def _load_background_shifters(self):
        self.bg_shifter_pattern_lo = to_16_bits((self.bg_shifter_pattern_lo & 0xFF00) | self.bg_next_tile_lsb)
        self.bg_shifter_pattern_hi = to_16_bits((self.bg_shifter_pattern_hi & 0xFF00) | self.bg_next_tile_msb)

        self.bg_shifter_attrib_lo  = to_16_bits(
            (self.bg_shifter_attrib_lo & 0xFF00) | (0xFF if (self.bg_next_tile_attrib & 0b01) else 0x00))

        self.bg_shifter_attrib_hi  = to_16_bits(
            (self.bg_shifter_attrib_hi & 0xFF00) | (0xFF if (self.bg_next_tile_attrib & 0b10) else 0x00))

    def _update_shifters(self):        
        if (self.mask.get_render_background()):
            self.bg_shifter_pattern_lo = to_16_bits(self.bg_shifter_pattern_lo << 1)
            self.bg_shifter_pattern_hi = to_16_bits(self.bg_shifter_pattern_hi << 1)
            self.bg_shifter_attrib_lo  = to_16_bits(self.bg_shifter_attrib_lo  << 1)
            self.bg_shifter_attrib_hi  = to_16_bits(self.bg_shifter_attrib_hi  << 1)

    def _increment_scroll_x(self):
        if self.mask.get_render_background() or self.mask.get_render_sprites():
            if self.vram_addr.get_coarse_x() == 31:
                self.vram_addr.set_coarse_x(0)
                self.vram_addr.set_nametable_x(~self.vram_addr.get_nametable_x())

            else: self.vram_addr.set_coarse_x(self.vram_addr.get_coarse_x() + 1)

    def _increment_scroll_y(self):
        if (self.mask.get_render_background() or self.mask.get_render_sprites()):
            if (self.vram_addr.get_fine_y() < 7): 
                self.vram_addr.set_fine_y(self.vram_addr.get_fine_y() + 1)

            else:
                self.vram_addr.set_fine_y(0)

                if self.vram_addr.get_coarse_y() == 29:
                    self.vram_addr.set_coarse_y(0)
                    self.vram_addr.set_nametable_y(~self.vram_addr.get_nametable_y())

                elif self.vram_addr.get_coarse_y() == 31: 
                    self.vram_addr.set_coarse_y(0)

                else: 
                    self.vram_addr.set_coarse_y(self.vram_addr.get_coarse_y() + 1)

    def _transfer_address_x(self):
        if (self.mask.get_render_background() or self.mask.get_render_sprites()):
            self.vram_addr.set_nametable_x(self.tram_addr.get_nametable_x())
            self.vram_addr.set_coarse_x(self.tram_addr.get_coarse_x())

    def _transfer_address_y(self):
        if (self.mask.get_render_background() or self.mask.get_render_sprites()):
            self.vram_addr.set_fine_y     (self.tram_addr.get_fine_y())
            self.vram_addr.set_nametable_y(self.tram_addr.get_nametable_y())
            self.vram_addr.set_coarse_y   (self.tram_addr.get_coarse_y())

    def clock(self):        
        if self.scanline >= -1 and self.scanline < 240:
            if self.scanline == 0  and self.cycle == 0: self.cycle = 1
        
            if self.scanline == -1 and self.cycle == 1: self.status.set_vertical_blank(0)
        
            if (self.cycle >= 2 and self.cycle < 258) or (self.cycle >= 321 and self.cycle < 338):
                self._update_shifters()

                value = (self.cycle - 1) % 8

                if value == 0:
                    self._load_background_shifters()
                    self.bg_next_tile_id = self.ppu_read(0x2000 | (self.vram_addr.reg & 0x0FFF))

                    #print(hex(self.bg_next_tile_id))

                elif value == 2:
                    self.bg_next_tile_attrib = self.ppu_read(
                        0x23C0 
                        | (self.vram_addr.get_nametable_y() << 11) 
                        | (self.vram_addr.get_nametable_x() << 10)
                        | ((self.vram_addr.get_coarse_y() >> 2) << 3) 
                        | (self.vram_addr.get_coarse_x() >> 2)
                    )

                    if (self.vram_addr.get_coarse_y() & 0x02): self.bg_next_tile_attrib >>= 4
                    if (self.vram_addr.get_coarse_x() & 0x02): self.bg_next_tile_attrib >>= 2

                    self.bg_next_tile_attrib &= 0x03

                elif value == 4:
                    self.bg_next_tile_lsb = self.ppu_read(
                        (self.control.get_pattern_background() << 12)
                      + (to_16_bits(self.bg_next_tile_id) << 4) + (self.vram_addr.get_fine_y()) + 0
                    )

                    #print("LSB: ", self.bg_next_tile_lsb)

                elif value == 6:
                    self.bg_next_tile_msb = self.ppu_read(
                        (self.control.get_pattern_background() << 12)
                      + (to_16_bits(self.bg_next_tile_id) << 4) + (self.vram_addr.get_fine_y()) + 8
                    )

                    #print("MSB: ", self.bg_next_tile_msb)

                elif value == 7: self._increment_scroll_x()

            if (self.cycle == 256): self._increment_scroll_y()

            if (self.cycle == 257):
                self._load_background_shifters()
                self._transfer_address_x()

            if (self.cycle == 338 or self.cycle == 340):
                self.bg_next_tile_id = self.ppu_read(0x2000 | (self.vram_addr.reg & 0x0FFF))

            if (self.scanline == -1 and self.cycle >= 280 and self.cycle < 305):
                self._transfer_address_y()
            
        if (self.scanline == 240): pass # Post Render Scanline - Do Nothing!
        
        if self.scanline >= 241 and self.scanline < 261:        
            if self.scanline == 241 and self.cycle == 1:
                #print("set_vertical_blank 1")
                self.status.set_vertical_blank(1)

                if self.control.get_enable_nmi(): self.nmi = True
        
        bg_pixel = 0x00
        bg_palette = 0x00

        if self.mask.get_render_background():
            bit_mux = to_16_bits(0x8000 >> self.fine_x)

            p0_pixel = to_8_bits((self.bg_shifter_pattern_lo & bit_mux) > 0)
            p1_pixel = to_8_bits((self.bg_shifter_pattern_hi & bit_mux) > 0)

            bg_pixel = to_8_bits((p1_pixel << 1) | p0_pixel)

            bg_pal0 = to_8_bits((self.bg_shifter_attrib_lo & bit_mux) > 0)
            bg_pal1 = to_8_bits((self.bg_shifter_attrib_hi & bit_mux) > 0)
            bg_palette = to_8_bits((bg_pal1 << 1) | bg_pal0)

        self.spr_screen.set_pixel(
            self.cycle - 1, self.scanline, self.get_colour_from_palette_ram(bg_palette, bg_pixel))

        #fake = 0x30
        #if int((n.random.rand() * 15)) % 2: fake = 0x3F
        #self.spr_screen.set_pixel( self.cycle - 1, self.scanline, self.pal_screen[fake])

        # Advance renderer - it never stops, it's relentless
        self.cycle += 1

        if self.cycle >= 341:
            self.cycle = 0
            self.scanline += 1

            if self.scanline >= 261:
                self.scanline = -1
                self.frame_complete = True

        if self.enable_log:
            print("Debug: ", end="")

            print(hex(self.bg_shifter_pattern_lo), " ", end="")
            print(hex(self.bg_shifter_pattern_hi), " ", end="")
            print(hex(self.bg_shifter_attrib_lo) , " ", end="")
            print(hex(self.bg_shifter_attrib_hi) , " ", end="")

            print(hex(self.bg_next_tile_id), " ", end="")
            print(hex(self.bg_next_tile_attrib), " ", end="")
            print(hex(self.bg_next_tile_lsb) , " ", end="")
            print(hex(self.bg_next_tile_msb) , " ", end="")

            print(hex(self.status.reg), " ", end="")
            print(hex(self.mask.reg), " ", end="")
            print(hex(self.control.reg) , " ", end="")
            print(hex(self.vram_addr.reg) , " ", end="")
            print(hex(self.tram_addr.reg), " ", end="")


            print(hex(self.fine_x), " ", end="")
            print(hex(self.address_latch), " ", end="")
            print(hex(self.ppu_data_buffer) , " ", end="")
            print(hex(self.scanline) , " ", end="")
            print(hex(self.cycle), " ")






