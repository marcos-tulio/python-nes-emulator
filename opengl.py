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

class CanvasOpenGL():
    pixel_size = 2
    sprite = nes.ppu.spr_screen

    key_value = 0x00

    ############################################################################################
    #                                       Frame
    ############################################################################################
    def __init__(self): pass

    def init_canvas(self):
        glutInit()
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
        glutInitWindowSize(
            self.sprite.width * self.pixel_size, self.sprite.height * self.pixel_size)
        self.window = glutCreateWindow("Python NES Emulator by Marcos Santos")

        glutDisplayFunc(self.refresh)
        glutKeyboardFunc(self.key_pressed)

        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        #glutMainLoop()
        
    def key_pressed(self, *args):
        self.key_value = 0x00

        if args[0] == b'w': self.key_value |= 0x08 # UP
        if args[0] == b's': self.key_value |= 0x04 # Down
        if args[0] == b'a': self.key_value |= 0x02 # Left
        if args[0] == b'd': self.key_value |= 0x01 # Right
        if args[0] == b'x': self.key_value |= 0x80 # X
        if args[0] == b'z': self.key_value |= 0x40 # Z
        if args[0] == b'c': self.key_value |= 0x20 # C
        if args[0] == b'v': self.key_value |= 0x10 # V

        #print("key: ", args[0], " controller: ", self.key_value)
        #elf.refresh()

    def close(self):
        if glutGetWindow():
            glutDestroyWindow(glutGetWindow())	
            glutMainLoopEvent()	
        
        glutMainLoopEvent()

    ############################################################################################
    #                                       Sprite
    ############################################################################################
    def loop(self, *args):
        self.draw_sprite(nes.ppu.spr_screen)
        glutTimerFunc(0, emulator._canvas.loop, 0)

    def refresh(self): pass
        #print("refresh")
        #self.draw_sprite(nes.ppu.spr_screen)
        #self.draw_sprite(nes.ppu.spr_screen)
        #self.update()
        #glutTimerFunc(17, self.refresh, 0);

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
        #gluOrtho2D(0, sprite.width, sprite.height, 0)

        fxs = fx = fys = fy = 0
        fxm = fym = 1

        if flip & g.Sprite.FLIP.HORIZ:
            fxs = sprite.width - 1
            fxm = -1

        if flip & g.Sprite.FLIP.VERT:
            fys = sprite.height - 1
            fym = -1

        data = [None, None, None, None] * (sprite.width * sprite.height)
        cont = 0
        
        # Fill buffer
        for i in range(sprite.height):      
            for j in range(sprite.width):                
                pixel = sprite.get_pixel(j, i) #change this to flip

                data[cont]     = pixel.r
                data[cont + 1] = pixel.g
                data[cont + 2] = pixel.b
                data[cont + 3] = pixel.a

                cont += 4

        # Reorder Pixels
        data = self.reorder_array(data, sprite.width * 4) # x4 = RGBA || change this to flip

        glPixelZoom(self.pixel_size, self.pixel_size)
        glDrawPixels(sprite.width, sprite.height, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glutSwapBuffers() 
        
        #glutPostRedisplay()
        #print("draw: ", sprite)

class Emulator():
    _thread = None
    _is_running = False 

    _canvas = None

    def start(self):
        if self._thread == None:
            #self._canvas = CanvasOpenGL()
            self._thread = th.Thread( target = self.loop )             
            self._thread.start()            

    def stop(self): self._is_running = False

    def loop(self):
        self._is_running = True
        #self._canvas.init_canvas()
        
        initial = datetime.now()

        frame_time = 1/60
        print(frame_time)

        print("In Loop...")

        wait_frames_for_key = 0

        while self._is_running:
            if  (datetime.now() - initial).total_seconds() >= .016:                
                if wait_frames_for_key > 0: wait_frames_for_key -= 1
                else: nes.controller[0] = 0x00

                nes.clock()
                while not nes.ppu.frame_complete: nes.clock()            
                nes.ppu.frame_complete = False               
                
                print("Proc. time: ", (datetime.now() - initial))
                initial = datetime.now()

            if not (self._canvas == None):
                if self._canvas.key_value != 0x00 and wait_frames_for_key == 0:
                    wait_frames_for_key = 1
                    nes.controller[0] = self._canvas.key_value
                    self._canvas.key_value = 0x00

        print("Emulator stopped!")
        self._thread = None

#######################
#       MAIN
#######################
cartridge = cart.Cartridge(rom)

nes.insert_cartridge(cartridge)

mapAsm = nes.cpu.disassemble(0x0000, 0xFFFF)

nes.reset()

emulator = Emulator()
emulator.start()

emulator._canvas = CanvasOpenGL()
emulator._canvas.init_canvas()

glutTimerFunc(17, emulator._canvas.loop, 0)
glutMainLoop()