from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
import bus
import sys

nes = bus.Bus()
mapAsm = []

class MainFrame(QWidget):
    def __init__(self):
        super().__init__()

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
    
        self.lbl_disassembly = []

    def keyPressEvent(self, event):
        if event.key() == 32:
            nes.cpu.clock()

            while not nes.cpu.complete():
                nes.cpu.clock()
            
            self.refreshRAM()
            self.refreshCPU()
            self.refreshCode()

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

    def drawCPUFlag(self, lbl, flag):
        lbl.setText(str(flag.name))

        if nes.cpu.status & flag:   
            lbl.setStyleSheet("color: green")
        else:
            lbl.setStyleSheet("color: red")

        return lbl

    def refreshCPUFlag(self):
        self.drawCPUFlag(self.lbl_cpu_n, bus.nes_cpu.OLC6502_FLAG.N)
        self.drawCPUFlag(self.lbl_cpu_v, bus.nes_cpu.OLC6502_FLAG.V)
        self.drawCPUFlag(self.lbl_cpu_u, bus.nes_cpu.OLC6502_FLAG.U)
        self.drawCPUFlag(self.lbl_cpu_b, bus.nes_cpu.OLC6502_FLAG.B)
        self.drawCPUFlag(self.lbl_cpu_d, bus.nes_cpu.OLC6502_FLAG.D)
        self.drawCPUFlag(self.lbl_cpu_i, bus.nes_cpu.OLC6502_FLAG.I)
        self.drawCPUFlag(self.lbl_cpu_z, bus.nes_cpu.OLC6502_FLAG.Z)
        self.drawCPUFlag(self.lbl_cpu_c, bus.nes_cpu.OLC6502_FLAG.C)

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

def frame():    
    app  = QApplication(sys.argv)

    window = MainFrame()
    window.setWindowTitle('Python NES Emulator by Marcos Santos')
    window.setFont(QFont("monospace", 10))

    vbox = QGridLayout()
    vbox.addWidget(window.initPanelRAM(), 0, 0, 2, 1)
    vbox.addWidget(window.initPanelCPU(), 0, 1, 1, 1)
    vbox.addWidget(window.initCode(15), 1, 1)

    window.refreshRAM()
    window.refreshCPU()
    window.refreshCode()

    window.setLayout(vbox)
    window.show()
    sys.exit(app.exec_())

#######################
#       MAIN
#######################
program = "A2 0A 8E 00 00 A2 03 8E 01 00 AC 00 00 A9 00 18 6D 01 00 88 D0 FA 8D 02 00 EA EA EA"
offset  = 0x8000

for x in program.split():
    nes.cpu_ram[offset] = hex(int(x, 16))
    offset += 1

# Set Reset Vector
nes.cpu_ram[0xFFFC] = 0x00
nes.cpu_ram[0xFFFD] = 0x80

mapAsm = nes.cpu.disassemble(0x0000, 0xFFFF)

nes.cpu.reset()

#print(mapAsm)

# Init frame
frame()

#print (nes.cpu.lookup[nes.cpu.opcode].addr_mode == nes.cpu.IMP)