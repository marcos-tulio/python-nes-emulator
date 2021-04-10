import bus
nes_bus = bus.Bus()

nes_bus.write(0x02, 0xFF)
nes_bus.cpu.clock()