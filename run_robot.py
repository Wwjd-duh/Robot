import time
from roboty import Robot


robo = Robot()

#robo.stop_all()
print("initializing all servos")
time.sleep(1)
print("Turning in one direction")
robo.set_waist(1)

