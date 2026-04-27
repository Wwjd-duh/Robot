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
# DETECTION SETTINGS
# -------------------------
FRONT_MIN_ANGLE = 330
FRONT_MAX_ANGLE = 30
FRONT_DIST_THRESHOLD = 600

LEFT_MIN_ANGLE = 260
LEFT_MAX_ANGLE = 290

RIGHT_MIN_ANGLE = 70
RIGHT_MAX_ANGLE = 100

MAX_VALID_DIST = 3000
SIDE_OPEN_AVG = 1600

DIRECTION = "unknown"

# -------------------------
# GENERIC HELPERS
# -------------------------
def in_angle_range(angle, min_angle, max_angle):
    if min_angle <= max_angle:
        return min_angle <= angle <= max_angle
    else:
        return angle >= min_angle or angle <= max_angle


def points_in_range(scan, min_angle, max_angle, max_dist):
    count = 0
    for _, angle, distance in scan:
        if in_angle_range(angle, min_angle, max_angle):
            if 0 < distance < max_dist:
                count += 1
    return count


def avg_distance(scan, min_angle, max_angle):
    distances = []

    for _, angle, distance in scan:
        if in_angle_range(angle, min_angle, max_angle):
            if 0 < distance < MAX_VALID_DIST:
                distances.append(distance)

    if len(distances) == 0:
        return 9999

    return sum(distances) / len(distances)


# -------------------------
# DETECTION FUNCTIONS
# -------------------------
def front_blocked(scan):
    blocked = points_in_range(scan, FRONT_MIN_ANGLE, FRONT_MAX_ANGLE, FRONT_DIST_THRESHOLD) > 5

    if blocked:
        left_avg = avg_distance(scan, LEFT_MIN_ANGLE, LEFT_MAX_ANGLE)
        right_avg = avg_distance(scan, RIGHT_MIN_ANGLE, RIGHT_MAX_ANGLE)

        print(f"FRONT BLOCKED | Left: {left_avg:.0f} mm | Right: {right_avg:.0f} mm")

    return blocked


def at_t_intersection(scan):
    if not front_blocked(scan):
        return False

    left_avg = avg_distance(scan, LEFT_MIN_ANGLE, LEFT_MAX_ANGLE)
    right_avg = avg_distance(scan, RIGHT_MIN_ANGLE, RIGHT_MAX_ANGLE)

    print(f"Left avg: {left_avg:.0f} mm | Right avg: {right_avg:.0f} mm")

    return left_avg > SIDE_OPEN_AVG and right_avg > SIDE_OPEN_AVG


# -------------------------
# DECIDE DIRECTION
# -------------------------
def decide_direction(user_input):
    global DIRECTION

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

    # TEMP INPUT
    reply = "take me to the bathroom please"
    decide_direction(reply)

    # Small initial turn
    robot.driveTr(0.5)
    time.sleep(2)
    robot.driveTr(0)

    robot.driveFB(-0.3)

    for scan in safe_scans():

        if at_t_intersection(scan):
            print("T intersection detected")
            robot.driveFB(0)
            break

        elif front_blocked(scan):
            print("Obstacle detected. Stopping.")
            robot.driveFB(0)

            # WAIT FOR CLEAR
            while True:
                scan = next_scan()
                if not front_blocked(scan):
                    break

                print("Waiting for obstacle to move...")
                time.sleep(0.2)

            print("Front clear. Continuing.")
            robot.driveFB(-0.3)

        else:
            print("Moving forward")

    # FINAL TURN
    if DIRECTION == "right":
        robot.driveTr(-0.3)
        time.sleep(2)
        robot.driveTr(0)
        engine.say("Sir, the robotics lab is here")

    elif DIRECTION == "left":
        robot.driveTr(0.3)
        time.sleep(2)
        robot.driveTr(0)
        engine.say("Sir, the bathroom is here")

    else:
        engine.say("I am not sure how we got here")

    engine.runAndWait()


# -------------------------
# SAFE LIDAR LOOP
# -------------------------
def safe_scans():
    while True:
        try:
            for scan in lidar.iter_scans():
                yield scan
        except Exception as e:
            print("LiDAR error:", e)
            try:
                lidar.stop()
                time.sleep(0.5)
            except:
                pass
            time.sleep(0.5)


# Helper to safely get ONE scan
def next_scan():
    return next(safe_scans())


# -------------------------
# MAIN LOOP
# -------------------------
def main():
    print("Robot idle. Waiting for human...")

    try:
        for scan in safe_scans():

            if front_blocked(scan):
                start_assistant()
                time.sleep(3)

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