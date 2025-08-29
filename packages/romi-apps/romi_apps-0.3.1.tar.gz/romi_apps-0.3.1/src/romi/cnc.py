import argparse
import time
from rcom.rcom_client import RcomWSClient

class CNC():

    @staticmethod
    def create(topic, id = None, registry_ip = None):
        client = RcomWSClient(topic, id, registry_ip)
        return CNC(client)
        
    def __init__(self, client):
        self.client = client
       
    def homing(self):
        self.client.execute('cnc-homing')
       
    def set_relay(self, index, value):
        params = {'index': index, 'value': value }
        self.client.execute('set-relay', params)
       
    def power_up(self):
        self.client.execute('power-up')
        
    def power_down(self):
        self.client.execute('power-down')
       
    def get_range(self):
        return self.client.execute('cnc-get-range')
       
    def moveto(self, x, y, z, speed, sync=True):
        params = {}
        if x != None:
            params["x"] = x
        if y != None:
            params["y"] = y
        if z != None:
            params["z"] = z
        if speed != None:
            params["speed"] = speed
        params["sync"] = sync
        self.client.execute('cnc-moveto', params)

    def current_theta(self):
        position = self.get_position()
        return position['z']

    def get_absolute_theta(self, theta):
        return theta + self.current_theta()
       
    def helix(self, xc, yc, alpha, z, speed, sync=True):
        params = { "xc": xc, "yc": yc, "z": z, "alpha": alpha, "speed": speed }
        self.client.execute('cnc-helix', params)
       
    def get_position(self):
        return self.client.execute('cnc-get-position')
       
    def synchronize(self, timeout_seconds):
        return self.client.execute('cnc-synchronize', {'timeout': timeout_seconds})

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', type=str, nargs='?', default="cnc",
                    help='The regsitry topic')
    args = parser.parse_args()

    cnc = CNC.create(args.topic)
    
    # Turn off battery charger
    cnc.set_relay(0, True)
    cnc.power_up()
    # Move to 1 meter
    cnc.moveto(1.0, 0, 0, 0.75)
    time.sleep(1)
    # Return to 4 cm before the homing
    cnc.moveto(0.04, 0, 0, 0.75)
    # Do homing
    #cnc.homing()
    cnc.power_down()
    # Recharge the battery
    cnc.set_relay(0, False)
