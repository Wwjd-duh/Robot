
import time
import maestro

# -------------------------
# Motor (one physical motor)
# -------------------------
class Motor:
    def __init__(self, controller, port):
        self.controller = controller
        self.port = port
        self.speed = 0

    def stop(self):
        self.controller.setTarget(self.port, 6000)

    def set_speed(self, speed):
        """
        Set motor speed.
        speed: float from -1.0 (full reverse) to 1.0 (full forward)
        """
        # Clamp speed to valid range
        speed = max(-1.0, min(1.0, speed))
        self.speed = speed

        # Map speed to Maestro target
        center = 6000      # typical stop/neutral
        range_ = 2000      # adjust as needed for your motor
        target = int(center + speed * range_)

        # Send command to Maestro
        self.controller.setTarget(self.port, target)



joint_num = 0
for i in range(17):
    j1 = Motor(maestro.Controller(), i)
    print("moving servo#", joint_num)
    j1.stop()
    time.sleep(2)
    j1.set_speed(0.75)
    time.sleep(1)
    j1.set_speed(-0.75)
    time.sleep(1)
    j1.stop()
    joint_num = joint_num + 1
#This is documentation
# port 0 is both wheels, positive is backwards, negetive is forwards
# port 1 is wheels go oposite directions. positive is left, negetive is right
# port 2 is waist, this does not work right now.
# port 3 is tilt head, positive is down
# port 4 is  pan head, positive is left and negetive is right
# port 5 is right shoulder and goes up and down
# port 6 is rightelbow side to side.
# port 7 is right elbow up and down
# port 8 is right wrist up and down
# port 9 is right wrist twist
# port 10 is right clamp open and shut, positive is close, negetive is open
# port 11 is left arm up and down, might be broken
# port 12 is left shoulder side to side.
# port 13 is left elbow up and down
# port 14 is left wrist up and down
# port 15 is left wrist twist
# port 16 is left clamp, same as right clamp but might be broken
