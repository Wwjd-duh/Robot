from adafruit_rplidar import RPLidar
from roboty import Robot
import time

PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME, timeout=3)
robot = Robot()

# Angles
FRONT_MIN_ANGLE = 330
FRONT_MAX_ANGLE = 30

# You said left wall angles were flipped,
# so adjust these if needed
LEFT_MIN_ANGLE = 240
LEFT_MAX_ANGLE = 300

FRONT_DIST_THRESHOLD = 500
LEFT_DIST_THRESHOLD = 600

last_command = None


def do_command(command):
    global last_command

    # Do not repeat same command over and over
    if command == last_command:
        return

    last_command = command

    if command == "GO_STRAIGHT":
        print("COMMAND: go straight")
        robot.driveTr(0)
        time.sleep(0.5)
        robot.driveFB(0.4)

    elif command == "TURN_RIGHT":
        print("COMMAND: turn right")
        robot.driveFB(0)
        time.sleep(0.5)
        robot.driveTr(-0.5)   # negative = right

    elif command == "SEARCH_LEFT":
        print("COMMAND: search for left wall")
        robot.driveFB(0)
        time.sleep(0.5)
        robot.driveTr(0.35)   # positive = left

    elif command == "STOP":
        print("COMMAND: stop")
        robot.driveFB(0)
        robot.driveTr(0)


try:
    for scan in lidar.iter_scans():
        front_wall = False
        left_wall = False

        for (_, angle, distance) in scan:

            # FRONT CHECK
            if (angle >= FRONT_MIN_ANGLE) or (angle <= FRONT_MAX_ANGLE):
                if distance < FRONT_DIST_THRESHOLD:
                    front_wall = True

            # LEFT CHECK
            if LEFT_MIN_ANGLE <= angle <= LEFT_MAX_ANGLE:
                if distance < LEFT_DIST_THRESHOLD:
                    left_wall = True

        if left_wall and front_wall:
            do_command("TURN_RIGHT")

        elif left_wall and not front_wall:
            do_command("GO_STRAIGHT")

        elif not left_wall:
            do_command("SEARCH_LEFT")

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Stopping...")
    do_command("STOP")
    lidar.stop()
    lidar.disconnect()