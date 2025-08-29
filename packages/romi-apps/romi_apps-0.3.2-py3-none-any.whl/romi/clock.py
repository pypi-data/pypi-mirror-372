import time
from rcom.rcom_client import RcomWSClient

class Clock():

    @staticmethod
    def create(topic = 'clock', registry_ip = None):
        client = RcomWSClient(topic, topic, registry_ip)
        return Clock(client)
   
    def __init__(self, client):
        self.client = client
       
    def get_time(self):
        return self.client.execute('get-time')

        
if __name__ == '__main__':
    
    clock = Clock.create()
    print(clock.get_time())
