import argparse
import time
from romi.cnc import CNC

class PlantScannerV3():

    def __init__(self, camera_topic = 'camera', cnc_topic = 'cnc'):
        self.cnc = CNC.create(cnc_topic)
        self.camera = Camera.create(camera_topic)

    def scan(self, radius, count):
        self.cnc.power_up()
        self.cnc.homing()
        
        dimension = self.cnc.get_range()
        print(f"dimension={dimension}")

        xc = (dimension[0][0] + dimension[0][1]) / 2.0
        yc = (dimension[1][0] + dimension[1][1]) / 2.0
        d = min(dimension[0][1] - dimension[0][0],
                dimension[1][1] - dimension[1][0])
        if (2.0 * radius > d):
            raise ValueError(f"Radius {radius} larger than maximum available space {d/2.0}")
        print(f"c=({xc}, {yc}), r={radius}")

        self.cnc.moveto(xc - radius, yc, 0.0, 0.5)

        position = self.cnc.get_position()
        print(f"position={position}")
    
        delta_alpha = -2.0 * math.pi / count
        start_time = time.time()
        for i in range(n):
            self.grab(i, i * delta_alpha)
            self.cnc.helix(xc, yc, delta_alpha, delta_alpha, 1.0)

        print(f"duration: {time.time()-start_time}")
        self.cnc.moveto(0.01, 0.01, 0.0, 0.5)
        self.cnc.homing()
        self.cnc.power_down()

    def grab(self, index, angle):
        filename = f"cablebot-{index:05d}-{int(10*angle):05d}.jpg"
        image = self.camera.grab()
        if image != None:
            print(f"Saving {filename}")
            image.save(filename)
        else:
            print(f"Failed: {filename}")
        
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--radius', type=float, nargs='?', default=0.3,
                    help='The radius of the scanning circle')
    parser.add_argument('--count', type=int, nargs='?', default="36",
                    help='The number of images')
    args = parser.parse_args()

    scanner = PlantScannerV3(args.radius, args.count)
    scanner.scan()

