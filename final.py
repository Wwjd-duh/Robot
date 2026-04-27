import time
from adafruit_rplidar import RPLidar
from roboty import Robot
import pyttsx3

# -------------------------
# SETUP
# -------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 130)
engine.setProperty('volume', 1.0)

PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME, timeout=3)

robot = Robot()
robot.center_all()

# -------------------------
# FRONT DETECTION SETTINGS
# -------------------------
FRONT_MIN_ANGLE = 330
FRONT_MAX_ANGLE = 30
FRONT_DIST_THRESHOLD = 600  # mm

LEFT_MIN_ANGLE = 240
LEFT_MAX_ANGLE = 300
LEFT_DIST_THRESHOLD = 1220

RIGHT_MIN_ANGLE = 60
RIGHT_MAX_ANGLE = 120
RIGHT_DIST_THRESHOLD = 1220

DIRECTION = "unknown"

# -------------------------
# CHECK IF FRONT IS BLOCKED
# -------------------------
def front_blocked(scan):
    count = 0
    for quality, angle, distance in scan:
        if angle >= FRONT_MIN_ANGLE or angle <= FRONT_MAX_ANGLE:
            if 0 < distance < FRONT_DIST_THRESHOLD:
                count += 1
    return count > 5  # 🔥 noise filter


def left_blocked(scan):
    count = 0
    for quality, angle, distance in scan:
        if LEFT_MIN_ANGLE <= angle <= LEFT_MAX_ANGLE:  # 🔥 fixed
            if 0 < distance < LEFT_DIST_THRESHOLD:
                count += 1
    return count > 5


def right_blocked(scan):
    count = 0
    for quality, angle, distance in scan:
        if RIGHT_MIN_ANGLE <= angle <= RIGHT_MAX_ANGLE:  # 🔥 fixed
            if 0 < distance < RIGHT_DIST_THRESHOLD:
                count += 1
    return count > 5

# -------------------------
# DECIDE DIRECTION
# -------------------------
def decide_direction(user_input):
    global DIRECTION  # very very important

    user_input = user_input.lower()

    if "robotics" in user_input or "lab" in user_input:
        DIRECTION = "right"
        engine.say("Right away sir, off to the place of my conception!")
    elif "bathroom" in user_input:
        DIRECTION = "left"
        engine.say("Right away sir, off to the privy.")
    else:
        DIRECTION = "unknown"
        engine.say("I beg your pardon master, please repeat that again.")

    engine.runAndWait()

def at_t_intersection(scan):
    front = front_blocked(scan)
    left = left_blocked(scan)
    right = right_blocked(scan)

    if front and not left and not right:
        return True

    return False

# -------------------------
# ASSISTANT BEHAVIOR
# -------------------------
def start_assistant():
    global DIRECTION

    print("Human detected. Starting assistant.")

    robot.stop_all()

    engine.say("Hello sir, where might I lead you today?")
    engine.runAndWait()
    time.sleep(0.5)

    # 🔥 replace this later with real input
    reply = "take me to the bathroom please"
    decide_direction(reply)

    # Turn a bit first
    robot.driveTr(0.5)
    time.sleep(2)
    robot.driveTr(0)

    # Move forward
    robot.driveFB(-0.3)

    #  IMPORTANT: get fresh scans while moving
    for scan in safe_scans():

        if at_t_intersection(scan):
            print("T intersection detected")
            robot.driveFB(0)
            break

        elif front_blocked(scan):
            print("Something is blocking the robot. Stopping.")
            robot.driveFB(0)

            # Wait until the front clears
            while front_blocked(scan):
                print("Waiting for obstacle to move...")
                time.sleep(0.2)
                scan = next(safe_scans())

            print("Front clear again. Continuing forward.")
            robot.driveFB(-0.3)

        else:
            print("Front is clear")

    # -------------------------
    # FINAL TURN BASED ON DIRECTION
    # -------------------------
    if DIRECTION == "right":
        time.sleep(0.25)
        robot.driveTr(-0.3)
        time.sleep(2)
        robot.driveTr(0)
        engine.say("Sir, the robotics lab is here")

    elif DIRECTION == "left":
        time.sleep(0.25)
        robot.driveTr(0.3)
        time.sleep(0.2)
        robot.driveTr(0)
        engine.say("Sir, the bathroom is here")

    else:
        engine.say("I am not sure how we got here")

    engine.runAndWait()

#This will help with the lidar errors
def safe_scans():
    while True:
        try:
            for scan in lidar.iter_scans():
                yield scan

        except Exception as e:
            print("LiDAR error ignored:", e)

            try:
                lidar.stop()
                time.sleep(0.5)
            except:
                pass

            time.sleep(0.5)

# -------------------------
# MAIN LOOP
# -------------------------
def main():
    print("Robot is idle. Waiting for human...")

    try:
        for scan in safe_scans():

            if front_blocked(scan):
                start_assistant()
                time.sleep(3)  # prevent instant retrigger

            else:
                robot.stop_all()

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopping program.")

    finally:
        robot.stop_all()
        lidar.stop()
        lidar.disconnect()

main()