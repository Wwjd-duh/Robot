import time
from adafruit_rplidar import RPLidar

PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME, timeout=3)

# -------------------------
# ANGLE SETTINGS
# -------------------------
FRONT_MIN_ANGLE = 330
FRONT_MAX_ANGLE = 30

LEFT_MIN_ANGLE = 240
LEFT_MAX_ANGLE = 300

RIGHT_MIN_ANGLE = 60
RIGHT_MAX_ANGLE = 120

# -------------------------
# DISTANCE SETTINGS
# -------------------------
FRONT_DIST_THRESHOLD = 700      # mm, object/wall close in front
SIDE_CLEAR_THRESHOLD = 1800     # mm, side average must be over this
MAX_SIDE_DISTANCE = 3000        # ignore anything farther than this

MIN_FRONT_POINTS = 5
MIN_SIDE_POINTS = 3


def angle_in_front(angle):
    return angle >= FRONT_MIN_ANGLE or angle <= FRONT_MAX_ANGLE


def front_blocked(scan):
    count = 0
    closest = None

    for quality, angle, distance in scan:
        if angle_in_front(angle):
            if 0 < distance < FRONT_DIST_THRESHOLD:
                count += 1

                if closest is None or distance < closest:
                    closest = distance

    return count > MIN_FRONT_POINTS, count, closest


def side_average(scan, min_angle, max_angle):
    distances = []

    for quality, angle, distance in scan:
        if min_angle <= angle <= max_angle:
            if 0 < distance <= MAX_SIDE_DISTANCE:
                distances.append(distance)

    if len(distances) < MIN_SIDE_POINTS:
        return None, len(distances)

    avg = sum(distances) / len(distances)
    return avg, len(distances)


def check_t_intersection(scan):
    front_is_blocked, front_count, front_closest = front_blocked(scan)

    if not front_is_blocked:
        return False, front_count, front_closest, None, None, 0, 0

    left_avg, left_count = side_average(scan, LEFT_MIN_ANGLE, LEFT_MAX_ANGLE)
    right_avg, right_count = side_average(scan, RIGHT_MIN_ANGLE, RIGHT_MAX_ANGLE)

    if left_avg is None or right_avg is None:
        return False, front_count, front_closest, left_avg, right_avg, left_count, right_count

    t_intersection = left_avg > SIDE_CLEAR_THRESHOLD and right_avg > SIDE_CLEAR_THRESHOLD

    return t_intersection, front_count, front_closest, left_avg, right_avg, left_count, right_count


try:
    print("Starting LiDAR T-intersection test...")
    time.sleep(2)

    for scan in lidar.iter_scans():
        (
            is_t_intersection,
            front_count,
            front_closest,
            left_avg,
            right_avg,
            left_count,
            right_count
        ) = check_t_intersection(scan)

        print("-------------")
        print(f"FRONT points:  {front_count}")
        print(f"FRONT closest: {front_closest} mm")

        print(f"LEFT avg:      {left_avg} mm")
        print(f"LEFT points:   {left_count}")

        print(f"RIGHT avg:     {right_avg} mm")
        print(f"RIGHT points:  {right_count}")

        if is_t_intersection:
            print("T INTERSECTION DETECTED")
        elif front_count > MIN_FRONT_POINTS:
            print("FRONT BLOCKED, but sides are not clear enough")
        else:
            print("FRONT CLEAR")

        time.sleep(0.25)

except KeyboardInterrupt:
    print("Stopping LiDAR...")

finally:
    lidar.stop()
    lidar.disconnect()
    print("LiDAR disconnected.")