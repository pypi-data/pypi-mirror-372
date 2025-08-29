from romi.camera import Camera
from romi.cnc import CNC

camera = Camera.create("camera")
cnc = CNC.create("cnc")
cnc.power_up()
cnc.homing()
for i in range(11):
    cnc.moveto(i * 0.05, 0, 0, 0.2)
    camera.grab().save(f"camera-linear-{i:02d}.jpg")
# Travel back, almost to zero, then do a homing
cnc.moveto(0.01, 0, 0, 0.2)
cnc.homing()
cnc.power_down()

