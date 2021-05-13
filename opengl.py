from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

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

class WorkFrame(QtCore.QThread):
    work = QtCore.pyqtSignal()

    def run(self): 
        self.stop = False

        global is_work_done
        is_work_done = True

        while not self.stop:
            if is_work_done: 
                is_work_done = False
                self.work.emit()

            time.sleep(.001)

class WorkScreen(QtCore.QThread):
    work = QtCore.pyqtSignal(object)
    canvas_is_opened = False

    def __init__(self, canvas_opengl):
        super().__init__()
        self.canvas_opengl = canvas_opengl

    def run(self): 
        self.canvas_opengl.init_canvas() 
        self.stop = False

        while not self.stop:
            self.canvas_opengl.refresh()
            time.sleep(.01)

        self.canvas_opengl.close()

class MainFrame(QWidget):
    selected_palette = 0

    def do_work(self):
        initial = datetime.now()
        
        nes.clock()
        while not nes.ppu.frame_complete: nes.clock()
        nes.ppu.frame_complete = False

        print("Proc. time: ", (datetime.now() - initial))

        self.refresh_cpu()
        self.refresh_code()

        if show_canvas_qt: self.canvas_qt.refresh(nes.ppu.spr_screen)
        else: self.refresh_ram()
        
        self.repaint()

        global is_work_done
        is_work_done = True

    #def paintEvent(self, event): print("chamou")

    def __init__(self):
        super().__init__()
        self.lbl_disassembly = []

    def keyPressEvent(self, event):
        #print("Key Pressed: " + str(event.key()))

        nes.controller[0] = 0x00

        if event.key() == 16777235: nes.controller[0] |= 0x08 # UP

        if event.key() == 16777237: nes.controller[0] |= 0x04 # Down

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

            nes.ppu.frame_complete = False
        
        elif event.key() == 80: # P
            self.selected_palette = (self.selected_palette + 1) & 0x07

        elif event.key() == 82: # R
            if show_palettes:
                for i in range(len(self.canvas_qt_pattern)):
                    self.canvas_qt_pattern[i].refresh(
                        nes.ppu.get_pattern_table(i, self.selected_palette))

            self.repaint()

        elif event.key() == 84: # T
            if emulator._is_running: emulator.stop()
            else: emulator.start()

        elif event.key() == 32: # Space
            if self.thread_code.isRunning(): self.thread_code.stop = True
            else: self.thread_code.start()

            if show_canvas_opengl: 
                if self.thread_canvas_opengl.isRunning(): self.thread_canvas_opengl.stop = True
                else: self.thread_canvas_opengl.start()

        self.refresh_cpu()
        self.refresh_code()

        if show_canvas_qt: self.canvas_qt.refresh(nes.ppu.spr_screen)
        else: self.refresh_ram()
        #self.canvas.refresh()

    ############################################################################################
    #                                   Code Debugger
    ############################################################################################
    def init_code(self, nLines):        
        vbox = QVBoxLayout()

        for i in range(nLines):
            self.lbl_disassembly.append(QLabel())
        
        for lbl in self.lbl_disassembly:
            vbox.addWidget(lbl)

        group = QGroupBox()
        group.setLayout(vbox)

        return group

    def refresh_code(self):
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

        if nes.cpu.status & flag: lbl.setStyleSheet("color: green")
        else: lbl.setStyleSheet("color: red")

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

    def refresh_cpu(self):
        self.refreshCPUFlag()
        self.lbl_cpu_pc.setText("PC: ${:04x} [{}]".format(nes.cpu.pcount, self.selected_palette).upper())
        self.lbl_cpu_a.setText("A: ${:02x} [{}]".format(nes.cpu.acc, nes.cpu.acc).upper())
        self.lbl_cpu_x.setText("X: ${:02x} [{}]".format(nes.cpu.reg_x, nes.cpu.reg_x).upper())
        self.lbl_cpu_y.setText("Y: ${:02x} [{}]".format(nes.cpu.reg_y, nes.cpu.reg_y).upper())
        self.lbl_cpu_stack.setText("Stack: ${:02x} [{}]" .format(nes.cpu.stack, nes.cpu.stack).upper())

    def init_panel_cpu(self):
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
    def draw_ram(self, lbl, addr, rows, cols):
        blob = ""
        for r in range(rows):
            blob += "${:04x}:  ".format(addr)

            for c in range(cols):
                blob += "{:02x} ".format(nes.cpuRead(addr, True))
                addr += 1

            blob += "\n"

        lbl.setText(blob.upper())

    def init_panel_ram(self):
        self.lbl_ram_low  = QLabel()
        self.lbl_ram_high = QLabel()

        vbox = QVBoxLayout()
        vbox.addWidget(self.lbl_ram_low)
        vbox.addWidget(self.lbl_ram_high)

        group = QGroupBox()
        group.setLayout(vbox)

        return group
    
    def refresh_ram(self):
        self.draw_ram(self.lbl_ram_low,  0x3F00, 16, 16)
        self.draw_ram(self.lbl_ram_high, 0x8000, 16, 16)

    ############################################################################################
    #                                       Canvas
    ############################################################################################
    def init_canvas_opengl(self):
        self.canvas_opengl = CanvasOpenGL()

    def init_canvas_qt(self, sprite, width, height):
        canvas_qt = CanvasQt(sprite = sprite)
        canvas_qt.setMinimumWidth(width)
        canvas_qt.setMinimumHeight(height)

        return canvas_qt

class CanvasQt(QWidget):
    is_repaint = False
    colors = {}
    pen = None

    def __init__(self, sprite, flip = g.Sprite.FLIP.NONE, scale = 2):
        super().__init__()
        self.sprite = sprite
        self._flip = flip
        self._scale = scale

    def refresh(self, sprite):
        self._x = 0
        self._y = 0
        self.sprite = sprite
        self.is_repaint = True
        self.update()

    def paintEvent(self, event):
        if not self.is_repaint: return
        self.is_repaint = False

        fxs = fx = 0
        fxm = 1

        fys = fy = 0
        fym = 1
        
        if self._flip & g.Sprite.FLIP.HORIZ:
            fxs = self.sprite.width - 1
            fxm = -1

        if self._flip & g.Sprite.FLIP.VERT:
            fys = self.sprite.height - 1
            fym = -1

        painter = QPainter()
        painter.begin(self)

        if not self.pen:
            self.pen = QPen()
            self.pen.setWidth(self._scale)

        fx = fxs
        for i in range(self.sprite.width):                
            fy = fys
            
            for j in range(self.sprite.height):
                pixel = self.sprite.get_pixel(fx, fy)  
                color = "{}_{}_{}".format(pixel.r, pixel.g, pixel.b)

                if not (color in self.colors):
                    self.colors[color] = QColor(pixel.r, pixel.g, pixel.b)
                    #print("Nova cor adicionada: ", color)
                
                #color = QColor(pixel.r, pixel.g, pixel.b)
                
                self.pen.setColor(self.colors[color])

                #painter.setPen(QPen(self.colors[color], self._scale))
                painter.setPen(self.pen)
                painter.drawPoint( self._scale * (self._x + i), self._scale * (self._y + j))

                fy += fym
            fx += fxm

        painter.end()
        return

class CanvasOpenGL():
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
        self.window = glutCreateWindow("Teste")
        glutDisplayFunc(self.init_canvas)

        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT)

    def close(self):
        if glutGetWindow():
            glutDestroyWindow(glutGetWindow())	
            glutMainLoopEvent()	
        
        glutMainLoopEvent()

    ############################################################################################
    #                                       Sprite
    ############################################################################################
    def refresh(self): self.draw_sprite(nes.ppu.spr_screen)

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
                pixel = sprite.get_pixel(fx, fy)

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

        while self._is_running:
            initial = datetime.now()

            nes.clock()
            while not nes.ppu.frame_complete: nes.clock()            
            nes.ppu.frame_complete = False

            #if  (datetime.now() - initial).total_seconds() > 1:
            #frame.canvas_qt.refresh( nes.ppu.spr_screen )

            print("Proc. time: ", (datetime.now() - initial))

        print("Emulator stopped!")
        self._thread = None

def init_frame():    
    app  = QApplication(sys.argv)

    global frame

    frame = MainFrame()
    frame.setWindowTitle('Python NES Emulator by Marcos Santos')
    frame.setFont(QFont("monospace", 10))

    grid = QGridLayout()

    if show_canvas_qt:
        frame.canvas_qt = frame.init_canvas_qt(nes.ppu.spr_screen, 500, 500)
        grid.addWidget(frame.canvas_qt, 0, 0, 2, 1)
        frame.canvas_qt.refresh(nes.ppu.spr_screen)
    
    else: 
        grid.addWidget(frame.init_panel_ram(), 0, 0, 2, 1)
        frame.refresh_ram()

    grid.addWidget(frame.init_panel_cpu(), 0, 1, 1, 1)
    grid.addWidget(frame.init_code(15), 1, 1)

    frame.refresh_cpu()
    frame.refresh_code()

    if show_palettes:
        frame.canvas_qt_pattern = [
            frame.init_canvas_qt(nes.ppu.get_pattern_table(0, frame.selected_palette), 300, 300),
            frame.init_canvas_qt(nes.ppu.get_pattern_table(1, frame.selected_palette), 300, 300)
        ]

        grid.addWidget(frame.canvas_qt_pattern[0], 0, 3, 3, 1)
        grid.addWidget(frame.canvas_qt_pattern[1], 1, 3, 3, 1)

        frame.canvas_qt_pattern[0].refresh(nes.ppu.get_pattern_table(0, frame.selected_palette))
        frame.canvas_qt_pattern[1].refresh(nes.ppu.get_pattern_table(1, frame.selected_palette))

    frame.thread_code = WorkFrame()
    frame.thread_code.work.connect(frame.do_work)

    if show_canvas_opengl:
        frame.canvas_opengl = CanvasOpenGL()
        frame.thread_canvas_opengl = WorkScreen(frame.canvas_opengl)

    frame.setLayout(grid)
    frame.show()

    emulator.start()

    sys.exit(app.exec_())

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
#

# Init frame
#init_frame()