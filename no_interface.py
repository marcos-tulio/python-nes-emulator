import threading as th
import time
from datetime import datetime

import bus
import sys
import cartridge as cart
import graphics as g

nes = bus.Bus()
cartridge = None

mapAsm = []

show_canvas_opengl = False
show_canvas_qt = True
show_palettes = False

rom = "nestest.nes"

class Emulator():
    _thread = None
    _is_running = False 

    def start(self):
        if self._thread == None:
            self._thread = th.Thread( target = self.loop )             
            self._thread.start()

    def stop(self): self._is_running = False

    def loop(self):
        self._is_running = True
        
        initial = datetime.now()

        cont = 0

        while self._is_running:
            initial = datetime.now()

            nes.clock()
            while not nes.ppu.frame_complete: nes.clock()            
            nes.ppu.frame_complete = False
            
            print(
                "Proc. time: ", (datetime.now() - initial).total_seconds(), 
                "clocks: ", nes.system_clock_counter
            )

            #exit()

        print("Emulator stopped!")
        self._thread = None

#######################
#       MAIN
#######################
cartridge = cart.Cartridge(rom)

nes.insert_cartridge(cartridge)

mapAsm = nes.cpu.disassemble(0x0000, 0xFFFF)

nes.reset()

global emulator
emulator = Emulator()
emulator.start()