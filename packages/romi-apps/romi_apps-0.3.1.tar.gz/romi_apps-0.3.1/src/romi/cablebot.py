import argparse
import time
from romi.cnc import CNC
from romi.camera import Camera

class Cablebot():

    def __init__(self, camera_topic = 'camera', cnc_topic = 'cnc'):
        self.cnc = CNC(cnc_topic, cnc_topic)
        self.camera = Camera(camera_topic, camera_topic)
    
    def startup_cnc(self):
        # Turn off the battery charger
        self.cnc.set_relay(0, True)
        # Power-up the motor
        self.cnc.power_up()
    
    def scan(self, x0, dx, count, no_homing=False):
        self.startup_cnc()
        for i in range(count + 1):
            x = x0 + i * dx
            self.cnc.moveto(x, 0, 0, 0.75)
            time.sleep(1)
            image = self.camera.grab()
            if image != None:
                filename = f"cablebot-{i:05d}-{int(1000*x):05d}.jpg"
                print(f"Saving {filename}")
                image.save(filename)
        self.shutdown_cnc(no_homing)
            
    def shutdown_cnc(self, no_homing):
        if no_homing:
            self.cnc.moveto(0.0, 0, 0, 0.75)
        else:
            # Return to 4 cm before the homing
            self.cnc.moveto(0.04, 0, 0, 0.75)
            self.cnc.homing()
        
        self.cnc.power_down()
        # Recharge the battery
        self.cnc.set_relay(0, False)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=float, nargs='?', default=0.0,
                    help='The start position')
    parser.add_argument('--interval', type=float, nargs='?', default=0.5,
                    help='The distance between camera positions')
    parser.add_argument('--count', type=int, nargs='?', default="1",
                    help='The number of images')
    parser.add_argument('--no-homing', action=argparse.BooleanOptionalAction,
                        help='Go back to zero without the homing procedure')
    args = parser.parse_args()

    cablebot = Cablebot()
    cablebot.scan(args.start, args.interval, args.count, args.no_homing)

    
