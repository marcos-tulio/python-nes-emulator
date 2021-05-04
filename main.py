from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

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

        while True:            
            nes.clock()
            while not nes.ppu.frame_complete: nes.clock()

            nes.clock()
            while not nes.cpu.complete(): nes.clock()

            self.refreshCPU()
            self.refreshCode()
            self.canvas.refresh()
            self.repaint()

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
            self.thread.start()
            #self.is_emulation_run = (not self.is_emulation_run)

        self.refreshCPU()
        self.refreshCode()
        self.canvas.refresh()

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
    class Canvas(QWidget):
        colors = {}
        pen = None

        def refresh(self):
            self._x = 0
            self._y = 0
            self._sprite = nes.ppu.spr_screen
            self._flip   = g.Sprite.FLIP.NONE
            self._scale = 3
            self.update()

        def paintEvent(self, event):
            fxs = fx = 0
            fxm = 1

            fys = fy = 0
            fym = 1
            
            if self._flip & g.Sprite.FLIP.HORIZ:
                fxs = self._sprite.width - 1
                fxm = -1

            if self._flip & g.Sprite.FLIP.VERT:
                fys = self._sprite.height - 1
                fym = -1

            painter = QPainter()
            painter.begin(self)

            if not self.pen:
                self.pen = QPen()
                self.pen.setWidth(self._scale)

            fx = fxs
            for i in range(self._sprite.width):                
                fy = fys
                
                for j in range(self._sprite.height):
                    pixel = self._sprite.get_pixel(fx, fy)  
                    color = "{}_{}_{}".format(pixel.r, pixel.g, pixel.b)

                    if not (color in self.colors):
                        self.colors[color] = QColor(pixel.r, pixel.g, pixel.b)
                        print("Nova cor adicionada: ", color)
                    
                    #color = QColor(pixel.r, pixel.g, pixel.b)
                    
                    self.pen.setColor(self.colors[color])

                    #painter.setPen(QPen(self.colors[color], self._scale))
                    painter.setPen(self.pen)
                    painter.drawPoint( self._scale * (self._x + i), self._scale * (self._y + j))

                    fy += fym
                fx += fxm

            painter.end()
            return

    def initPanelSprite(self, width, height):
        self.canvas = self.Canvas()
        self.canvas.setMinimumWidth(width)
        self.canvas.setMinimumHeight(height)
        return self.canvas

def frame():    
    app  = QApplication(sys.argv)

    window = MainFrame()
    window.setWindowTitle('Python NES Emulator by Marcos Santos')
    window.setFont(QFont("monospace", 10))
    
    vbox = QGridLayout()
    vbox.addWidget(window.initPanelSprite(500, 500), 0, 0, 2, 1)
    vbox.addWidget(window.initPanelCPU(), 0, 1, 1, 1)
    vbox.addWidget(window.initCode(15), 1, 1)

    #window.refreshRAM()
    window.refreshCPU()
    window.refreshCode()
    window.canvas.refresh()

    window.thread = QThread()
    window.thread.started.connect(window.do_work)

    window.setLayout(vbox)
    window.show()
    
    sys.exit(app.exec_())

#######################
#       MAIN
#######################
cartridge = cart.Cartridge("smb.nes")

nes.insert_cartridge(cartridge)

mapAsm = nes.cpu.disassemble(0x0000, 0xFFFF)

nes.reset()

# Init frame
frame()