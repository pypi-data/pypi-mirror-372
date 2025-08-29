from romi.cnc import CNC

cnc = CNC.create("cnc")
cnc.power_up()
cnc.homing()
cnc.moveto(0.2, 0, 0, 1)
cnc.homing()
cnc.power_down()

