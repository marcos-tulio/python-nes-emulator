from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from datetime import datetime, timedelta

import time
import threading

import bus
import sys
import cartridge as cart
import graphics as g

nes = bus.Bus()
cartridge = None

mapAsm = []

class MainFrame(QWidget):
    is_emulation_run = False
    thread = None

    def do_work(self):
        QThread.sleep(1)

        #before = datetime.now()
        while True:   

            nes.clock()
            while not nes.ppu.frame_complete: nes.clock()

            nes.clock()
            while not nes.cpu.complete(): nes.clock()

            self.refreshCPU()
            self.refreshCode()
            self.repaint()

            #time.sleep(1)

            #now = datetime.now()

            #if (now - before) > timedelta(milliseconds = 1000):
            #    before = now
            #    self.canvas.refresh()

            #QThread.sleep(.1)

    def __init__(self):
        super().__init__()

        '''
        self.lbl_ram_low  = None
        self.lbl_ram_high = None

        self.lbl_cpu_n = None
        self.lbl_cpu_v = None
        self.lbl_cpu_u = None
        self.lbl_cpu_b = None
        self.lbl_cpu_d = None
        self.lbl_cpu_i = None
        self.lbl_cpu_z = None
        self.lbl_cpu_c = None

        self.lbl_cpu_pc = None
        self.lbl_cpu_a = None
        self.lbl_cpu_x = None
        self.lbl_cpu_y = None
        self.lbl_cpu_stack = None
        '''

        self.lbl_disassembly = []

    def keyPressEvent(self, event):
        if event.key() == 67:   # C
            #print(self.canvas.colors)
            nes.clock()
            while not nes.cpu.complete(): nes.clock()

            nes.clock()
            while not nes.cpu.complete(): nes.clock()

        elif event.key() == 70: # F
            nes.clock()
            while not nes.ppu.frame_complete: nes.clock()

            nes.clock()
            while not nes.cpu.complete(): nes.clock()

        elif event.key() == 32: # Space
            #self.thread.start()
            self.thread_canvas.start()
            self.thread_code.start()

            self.thread_canvas.join()
            self.thread_code.join()
            #self.is_emulation_run = (not self.is_emulation_run)

        self.refreshCPU()
        self.refreshCode()
        #self.canvas.refresh()

    ############################################################################################
    #                                   Code Debugger
    ############################################################################################
    def initCode(self, nLines):        
        vbox = QVBoxLayout()

        for i in range(nLines):
            self.lbl_disassembly.append(QLabel())
        
        for lbl in self.lbl_disassembly:
            vbox.addWidget(lbl)

        group = QGroupBox()
        group.setLayout(vbox)

        return group

    def refreshCode(self):
        #nes.cpu.disassemble(0x0000, 0xFFFF)

        init = nes.cpu.pcount
        ins = ""
        for lbl in self.lbl_disassembly:
            while(True):
                try:
                    ins = mapAsm[init]
                    init += 1
                    break
                except:
                    pass

                init += 1

            lbl.setText(ins.upper())

    ############################################################################################
    #                                         CPU
    ############################################################################################
    def drawCPUFlag(self, lbl, flag):
        lbl.setText(str(flag.name))

        if nes.cpu.status & flag:   
            lbl.setStyleSheet("color: green")
        else:
            lbl.setStyleSheet("color: red")

        return lbl

    def refreshCPUFlag(self):
        self.drawCPUFlag(self.lbl_cpu_n, bus.nes_cpu.CPU6502_FLAG.N)
        self.drawCPUFlag(self.lbl_cpu_v, bus.nes_cpu.CPU6502_FLAG.V)
        self.drawCPUFlag(self.lbl_cpu_u, bus.nes_cpu.CPU6502_FLAG.U)
        self.drawCPUFlag(self.lbl_cpu_b, bus.nes_cpu.CPU6502_FLAG.B)
        self.drawCPUFlag(self.lbl_cpu_d, bus.nes_cpu.CPU6502_FLAG.D)
        self.drawCPUFlag(self.lbl_cpu_i, bus.nes_cpu.CPU6502_FLAG.I)
        self.drawCPUFlag(self.lbl_cpu_z, bus.nes_cpu.CPU6502_FLAG.Z)
        self.drawCPUFlag(self.lbl_cpu_c, bus.nes_cpu.CPU6502_FLAG.C)

    def getCPUAllFlags(self):
        self.lbl_cpu_n = QLabel()
        self.lbl_cpu_v = QLabel()
        self.lbl_cpu_u = QLabel()
        self.lbl_cpu_b = QLabel()
        self.lbl_cpu_d = QLabel()
        self.lbl_cpu_i = QLabel()
        self.lbl_cpu_z = QLabel()
        self.lbl_cpu_c = QLabel()

        layout = QHBoxLayout()
        layout.addWidget(self.lbl_cpu_n)
        layout.addWidget(self.lbl_cpu_v)
        layout.addWidget(self.lbl_cpu_u)
        layout.addWidget(self.lbl_cpu_b)
        layout.addWidget(self.lbl_cpu_d)
        layout.addWidget(self.lbl_cpu_i)
        layout.addWidget(self.lbl_cpu_z)
        layout.addWidget(self.lbl_cpu_c)

        flags = QGroupBox("Status:")
        flags.setLayout(layout)

        return flags

    def refreshCPU(self):
        self.refreshCPUFlag()
        self.lbl_cpu_pc.setText("PC: ${:04x} [{}]".format(nes.cpu.pcount, nes.cpu.cycles).upper())
        self.lbl_cpu_a.setText("A: ${:02x} [{}]".format(nes.cpu.acc, nes.cpu.acc).upper())
        self.lbl_cpu_x.setText("X: ${:02x} [{}]".format(nes.cpu.reg_x, nes.cpu.reg_x).upper())
        self.lbl_cpu_y.setText("Y: ${:02x} [{}]".format(nes.cpu.reg_y, nes.cpu.reg_y).upper())
        self.lbl_cpu_stack.setText("Stack: ${:04x} [{}]" .format(nes.cpu.stack, nes.cpu.stack).upper())

    def initPanelCPU(self):
        self.lbl_cpu_pc     = QLabel()
        self.lbl_cpu_a      = QLabel()
        self.lbl_cpu_x      = QLabel()
        self.lbl_cpu_y      = QLabel()
        self.lbl_cpu_stack  = QLabel()

        vbox = QVBoxLayout()
        vbox.addWidget(self.getCPUAllFlags())
        vbox.addWidget(self.lbl_cpu_pc)
        vbox.addWidget(self.lbl_cpu_a)
        vbox.addWidget(self.lbl_cpu_x)
        vbox.addWidget(self.lbl_cpu_y)
        vbox.addWidget(self.lbl_cpu_stack)

        group = QGroupBox()
        group.setLayout(vbox)

        return group

    ############################################################################################
    #                                         RAM
    ############################################################################################
    def drawRAM(self, lbl, addr, rows, cols):
        blob = ""
        for r in range(rows):
            blob += "${:04x}:  ".format(addr)

            for c in range(cols):
                blob += "{:02x} ".format(nes.cpuRead(addr, True))
                addr += 1

            blob += "\n"

        lbl.setText(blob.upper())

    def initPanelRAM(self):
        self.lbl_ram_low  = QLabel()
        self.lbl_ram_high = QLabel()

        vbox = QVBoxLayout()
        vbox.addWidget(self.lbl_ram_low)
        vbox.addWidget(self.lbl_ram_high)

        group = QGroupBox()
        group.setLayout(vbox)

        return group
    
    def refreshRAM(self):
        self.drawRAM(self.lbl_ram_low,  0x0000, 16, 16)
        self.drawRAM(self.lbl_ram_high, 0x8000, 16, 16)

    ############################################################################################
    #                                        Sprite
    ############################################################################################
    def initPanelSprite(self, width, height):
        self.canvas = Canvas()

class Canvas():
    pixel_size = 2
    sprite = nes.ppu.spr_screen

    ############################################################################################
    #                                       Frame
    ############################################################################################
    def __init__(self): pass

    def init_canvas(self):
        glutInit()
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
        glutInitWindowSize(
            self.sprite.width * self.pixel_size, self.sprite.height * self.pixel_size)
        glutCreateWindow("Teste")
        glutDisplayFunc(self.init_canvas)

        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT)

    def main_loop(self):
        self.init_canvas()        

        while True:
            self.refresh()
            time.sleep(.03)

    ############################################################################################
    #                                       Sprite
    ############################################################################################
    def refresh(self):
        self.draw_sprite(nes.ppu.spr_screen)

    def reorder_array(self, array, split = 0):
        temp = [None] * len(array)
        
        items_in_array = 0
        break_index = 1

        for item in array:
            if items_in_array == split:
                break_index += 1
                items_in_array = 0

            temp[len(temp) - (split * break_index) + items_in_array] = item
            items_in_array += 1

        return temp

    def draw_sprite(self, sprite, flip = g.Sprite.FLIP.NONE):
        gluOrtho2D(0, sprite.width, sprite.height, 0)

        fxs = fx = fys = fy = 0
        fxm = fym = 1

        if flip & g.Sprite.FLIP.HORIZ:
            fxs = sprite.width - 1
            fxm = -1

        if flip & g.Sprite.FLIP.VERT:
            fys = sprite.height - 1
            fym = -1

        data = [0, 0, 0, 0] * (sprite.width * sprite.height)
        cont = 0
        
        # Fill buffer
        fx = fxs
        for i in range(sprite.width):
            #cont = len(data) - ((sprite.height * 3) * (i + 1))
            
            fy = fys
            for j in range(sprite.height):                
                pixel = sprite.getPixel(fx, fy)

                data[cont]     = pixel.r
                data[cont + 1] = pixel.g
                data[cont + 2] = pixel.b
                data[cont + 3] = pixel.a

                cont += 4

                fy += fym
            fx += fxm

        # Reorder Pixels
        data = self.reorder_array(data, sprite.width * 4) # x4 = RGBA

        glPixelZoom(self.pixel_size, self.pixel_size)
        glDrawPixels(sprite.width, sprite.height, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glutSwapBuffers() 

def frame():    
    app  = QApplication(sys.argv)

    window = MainFrame()
    window.setWindowTitle('Python NES Emulator by Marcos Santos')
    window.setFont(QFont("monospace", 10))
    
    vbox = QGridLayout()
    #vbox.addWidget(window.initPanelSprite(500, 500), 0, 0, 2, 1)
    
    vbox.addWidget(window.initPanelCPU(), 0, 1, 1, 1)
    vbox.addWidget(window.initCode(15), 1, 1)

    #window.refreshRAM()
    window.refreshCPU()
    window.refreshCode()
    #window.canvas.refresh()

    #window.thread = QThread()
    #window.thread.started.connect(window.do_work)

    #window.initPanelSprite(500, 500)
    window.canvas = Canvas()

    window.thread_code = threading.Thread(target = window.do_work)
    window.thread_canvas = threading.Thread(target = window.canvas.main_loop)

    window.setLayout(vbox)
    window.show()
    
    sys.exit(app.exec_())

#######################
#       MAIN
#######################
cartridge = cart.Cartridge("nestest.nes")

nes.insertCartridge(cartridge)

mapAsm = nes.cpu.disassemble(0x0000, 0xFFFF)

nes.reset()

# Init frame
frame()