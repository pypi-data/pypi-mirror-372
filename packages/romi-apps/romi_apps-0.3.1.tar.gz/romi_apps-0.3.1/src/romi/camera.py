import time
import websocket
from PIL import Image
from io import BytesIO
from rcom.rcom_client import RcomWSClient
import argparse

class Camera():

    @staticmethod
    def create(topic, registry_ip = None):
        client = RcomWSClient(topic, topic, registry_ip)
        return Camera(client)
   
    def __init__(self, client):
        self.client = client
       
    def grab(self):
        cmd = f'{{"method": "camera:grab-jpeg-binary", "id": "{self.client.id}"}}'
        data = self.client.binary(cmd)
        print(f'data length {len(data)}')
        with open("tmp.jpg", "wb") as f:
            f.write(data)
        return Image.open(BytesIO(data))

    def set_value(self, name, value):
        params = {'name': name, 'value': value}
        self.client.execute('camera:set-value', params)

    def select_option(self, name, value):
        params = {'name': name, 'value': value}
        self.client.execute('camera:select-option', params)
        
    def get_camera_info(self):
        return self.client.execute('camera:get-camera-info')
       
    def power_up(self):
        self.client.execute('power-up')
        
    def power_down(self):
        self.client.execute('power-down')


class FakeCamera():
    
    def __init__(self, filepath):
        self.image = Image.open(filepath)
       
    def grab(self):
        return self.image

    def set_value(self, name, value):
        params = {'name': name, 'value': value}
        print(f'camera:set-value: {name}={value}')

    def select_option(self, name, value):
        params = {'name': name, 'value': value}
        print(f'camera:select-option: {name}={value}')
       
    def power_up(self):
        #print(f'power-up')
        pass
        
    def power_down(self):
        #print(f'power-down')
        pass

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', type=str, nargs='?', default="camera",
                        help='The registry topic')
    parser.add_argument('--file', type=str, nargs='?', default="test.jpg",
                        help='The file for the fake camera')
    parser.add_argument('--registry', type=str, nargs='?', default=None,
                        help='The IP address of the registry')
    parser.add_argument('--count', type=int, nargs='?', default=10,
                        help='The number of images')
    parser.add_argument('--sleep', type=float, nargs='?', default=0.0,
                        help='The delay between images')
    args = parser.parse_args()
    
    camera = Camera.create(args.topic, args.registry)
    for i in range(args.count):
        image = camera.grab()
        if image != None:
            print(f"Saving {args.topic}-{i:05d}.jpg")
            image.save(f"{args.topic}-{i:05d}.jpg")
        time.sleep(args.sleep)
        
