import time
from rcom.rcom_client import RcomWSClient
import argparse


class Battery():

    @staticmethod
    def create(topic, registry_ip = None):
        client = RcomWSClient(topic, topic, registry_ip)
        return Battery(client)
   
    def __init__(self, client):
        self.client = client
        
    def is_charging(self):
        return self.client.execute('battery:is-charging')
        
    def get_voltage(self):
        return self.client.execute('battery:get-voltage')
        
    def get_current(self):
        return self.client.execute('battery:get-current')

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', type=str, nargs='?', default="battery",
                        help='The registry topic')
    parser.add_argument('--registry', type=str, nargs='?', default=None,
                        help='The IP address of the registry')
    args = parser.parse_args()
    
    battery = Battery.create(args.topic, args.registry)
    while True:
        print(f"Charging: {battery.is_charging()}")
        print(f"Voltage:  {battery.get_voltage()} V")
        print(f"Current:  {battery.get_current()} A")
        print(f"Level:    {100.0 * battery.get_level()} %")
        time.sleep(1)
