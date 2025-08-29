import argparse
import time
from rcom.rcom_client import RcomWSClient

class DCMotors():

    @staticmethod
    def create(topic, id = None, registry_ip = None):
        client = RcomWSClient(topic, id, registry_ip)
        return CNC(client)
        
    def __init__(self, client):
        self.client = client
       
    def power_up(self):
        self.client.execute('power-up')
        
    def power_down(self):
        self.client.execute('power-down')
       
    def moveat(self, left, right):
        params = {"left": left, "right": right}
        self.client.execute('navigation-moveat', params)

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', type=str, nargs='?', default="motors",
                    help='The regsitry topic')
    args = parser.parse_args()

    motors = DCMotors.create(args.topic)
    
    cnc.power_up()
    cnc.moveat(1.0, 0, 0, 0.75)
