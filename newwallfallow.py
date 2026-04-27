import time
from adafruit_rplidar import RPLidar
from roboty import Robot

# -------------------------
# SETUP
# -------------------------
PORT_NAME = "/dev/ttyUSB0"
lidar = RPLidar(None, PORT_NAME, timeout=3)

robot = Robot()
robot.center_all()

# -------------------------
# SETTINGS
# -------------------------
FRONT_MIN_ANGLE = 330
FRONT_MAX_ANGLE = 30
FRONT_DIST_THRESHOLD = 650

LEFT_MIN_ANGLE = 260
LEFT_MAX_ANGLE = 290

MAX_VALID_DIST = 3000

# Wall following tuning
LEFT_TOO_CLOSE = 500
LEFT_GOOD_MIN = 650
LEFT_GOOD_MAX = 950
LEFT_TOO_FAR = 1200

FORWARD_SPEED = -0.30

# Robot directions
TURN_RIGHT = -0.30
TURN_LEFT = 0.30

# -------------------------
# LIDAR HELPERS
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


def front_blocked(scan):
    return points_in_range(scan, FRONT_MIN_ANGLE, FRONT_MAX_ANGLE, FRONT_DIST_THRESHOLD) > 5


def left_distance(scan):
    return avg_distance(scan, LEFT_MIN_ANGLE, LEFT_MAX_ANGLE)


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


# -------------------------
# MOVEMENT HELPERS
# -------------------------
def stop():
    robot.driveFB(0)
    robot.driveTr(0)


def move_forward():
    robot.driveFB(FORWARD_SPEED)
    robot.driveTr(0)


def turn_right_for(seconds):
    robot.driveFB(0)
    robot.driveTr(TURN_RIGHT)
    time.sleep(seconds)
    robot.driveTr(0)


def turn_left_slight():
    robot.driveFB(FORWARD_SPEED)
    robot.driveTr(TURN_LEFT)


def turn_right_slight():
    robot.driveFB(FORWARD_SPEED)
    robot.driveTr(TURN_RIGHT)


# -------------------------
# MAIN LOGIC
# -------------------------
def main():
    print("Starting wall follower (LEFT wall, turning RIGHT around room)")

    try:
        # STEP 1: Move forward until wall
        robot.driveFB(FORWARD_SPEED)

        for scan in safe_scans():
            if front_blocked(scan):
                print("Front wall detected → turning right")
                stop()
                time.sleep(0.3)
                turn_right_for(2.0)
                break

        print("Now following LEFT wall")

        # STEP 2: Follow LEFT wall
        for scan in safe_scans():
            front = front_blocked(scan)
            left = left_distance(scan)

            print(f"Front: {front} | Left distance: {left:.0f} mm")

            if front:
                print("Wall ahead → turning right")
                stop()
                time.sleep(0.2)
                turn_right_for(1.5)

            elif left < LEFT_TOO_CLOSE:
                print("Too close to left wall → steer RIGHT")
                turn_right_slight()

            elif left > LEFT_TOO_FAR:
                print("Too far from left wall → steer LEFT")
                turn_left_slight()

            else:
                print("Good distance → forward")
                move_forward()

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopping")

    finally:
        stop()
        lidar.stop()
        lidar.disconnect()


main()