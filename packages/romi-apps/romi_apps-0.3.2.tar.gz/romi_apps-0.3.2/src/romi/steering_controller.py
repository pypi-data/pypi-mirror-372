import serial
import json
import math
import time

from romiserial.device import RomiDevice

class SteeringController(RomiDevice):

    def __init__(self, device, config): 
        super(SteeringController, self).__init__(device)
        self.set_configuration(config)
        # angle values in degrees
        self.stepper_angle_left = 0
        self.stepper_angle_right = 0
        self.encoder_angle_left = 0
        self.encoder_angle_right = 0
        self.target_angle_left = 0
        self.target_angle_right = 0
        # angle values in steps
        self.stepper_left = 0
        self.stepper_right = 0
        self.encoder_position_left = 0
        self.encoder_position_right = 0
        
    def set_configuration(self, config):
        self.config = config
        self.__send_configuration(config)
        
    def __send_configuration(self, config):
        self.stepper_steps = config["stepper_steps"]
        self.encoder_steps = config["encoder_steps"]
        stepper_steps_hi = int(self.stepper_steps / 1000) 
        stepper_steps_lo = int(self.stepper_steps % 1000) 
        encoder_steps_hi = int(self.encoder_steps / 1000) 
        encoder_steps_lo = int(self.encoder_steps % 1000) 
        return self.execute("C", stepper_steps_hi, stepper_steps_lo,
                            encoder_steps_hi, encoder_steps_lo)
        
    def enable(self):
        self.send_command("E[1]")
    
    def disable(self):
        self.send_command("E[0]")

    def get_info(self):
        return self.send_command("?")

    def get_info(self):
        return self.send_command("?")
    
    def moveto(self, left_angle, right_angle):
        """ Set the angles in degrees """
        if left_angle < -180 or left_angle > 180:
            raise ValueError(f"Left angle out of bounds [-180,180]: {left_angle}")
        if right_angle < -180 or right_angle > 180:
            raise ValueError(f"Right angle out of bounds [-180,180]: {right_angle}")
        left_value = int(left_angle * 10)
        right_value = int(right_angle * 10)
        return self.execute("m", left_value, right_value)
        
    def __update_status(self):
        data = self.send_command("P")
        print(data)

    def get_positions(self):
        data = self.send_command("P")
        stepper_angle_left = data[1] / 10.0;
        stepper_angle_right = data[2] / 10.0;
        encoder_angle_left = data[3] / 10.0;
        encoder_angle_right = data[4] / 10.0;
        target_angle_left = data[5] / 10.0;
        target_angle_right = data[6] / 10.0;
        stepper_position_left = data[7];
        stepper_position_right = data[8];
        encoder_position_left = data[9];
        encoder_position_right = data[10];
        return {
            "stepper_angle": [stepper_angle_left, stepper_angle_right],
            "encoder_angle": [encoder_angle_left, encoder_angle_right],
            "target_angle": [target_angle_left, target_angle_right],
            "stepper_position": [stepper_position_left, stepper_position_right],
            "encoder_position": [encoder_position_left, encoder_position_right]
        }

    def set_mode(self, mode): # 0=open-loop, 1=closed-loop
        return self.execute("L", mode)
        
        
if __name__ == '__main__':
    config = {
        "stepper_steps": 15300,
        #"stepper_steps": 200,
        "encoder_steps": 1024
    }
    steering = SteeringController("/dev/ttyACM0", config)
    print(steering.get_info())

    test = 6
    
    # Test 1: move encoder to check positions and angles
    # Use TestController on the Arduino
    if test == 1:
        steering.disable()
        for i in range(120):
            positions = steering.get_positions()
            print(positions)
            time.sleep(2)

    # Test 2: move steppers
    # Use TestController on the Arduino
    if test == 2:
        steering.enable()
        for i in range(120):
            positions = steering.get_positions()
            print(positions)
            time.sleep(2)

    # Test 3: steppers follow encoder
    # Use FollowController on the Arduino
    if test == 3:
        steering.enable()
        for i in range(120):
            positions = steering.get_positions()
            print(positions)
            time.sleep(2)

    # Test 4: open loop control
    # Use Controller on the Arduino
    if test == 4:
        steering.set_mode(0)
        steering.enable()
        steering.moveto(90, 90)
        for i in range(120):
            positions = steering.get_positions()
            print(positions)
            time.sleep(2)

    # Test 5: open loop control
    # Use Controller on the Arduino
    if test == 5:
        steering.set_mode(0)
        steering.enable()
        steering.moveto(-90, -90)
        for i in range(120):
            positions = steering.get_positions()
            print(positions)
            time.sleep(2)

    # Test 6: closed loop control
    # Use Controller on the Arduino
    if test == 6:
        steering.enable()
        steering.moveto(10, 10)
        time.sleep(2)
        steering.moveto(-10, -10)
        time.sleep(2)
        steering.moveto(0, 0)
        time.sleep(1)
#        for i in range(10):
#            print(steering.get_positions())
#            time.sleep(1)
#        steering.moveto(-10, -10)
#        for i in range(20):
#            print(steering.get_positions())
#            time.sleep(1)
#        steering.moveto(0, 0)
#        for i in range(10):
#            print(steering.get_positions())
#            time.sleep(1)
    
    steering.disable()
