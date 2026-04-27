#from rplidar import RPLidar, RPLidarException
from adafruit_rplidar import RPLidar
from math import cos, sin, pi, floor

PORT_NAME = '/dev/ttyUSB0'
lidar = RPLidar(None, PORT_NAME, timeout=3)

# Define angle ranges (degrees)
FRONT_MIN_ANGLE = 330
FRONT_MAX_ANGLE = 30

BACK_MIN_ANGLE = 150
BACK_MAX_ANGLE = 210

# Distance threshold (mm)
DIST_THRESHOLD = 500  # adjust as needed

try:
    for scan in lidar.iter_scans():
        front_blocked = False
        back_blocked = False

        for (_, angle, distance) in scan:

            # --- FRONT CHECK ---
            if ((angle >= FRONT_MIN_ANGLE) or (angle <= FRONT_MAX_ANGLE)):
                if distance < DIST_THRESHOLD:
                    front_blocked = True

            # --- BACK CHECK ---
            if (BACK_MIN_ANGLE <= angle <= BACK_MAX_ANGLE):
                if distance < DIST_THRESHOLD:
                    back_blocked = True

        # Print results once per scan
        if front_blocked:
            print("Front is BLOCKED")
        else:
            print("Front is clear")

        if back_blocked:
            print("Back is BLOCKED")
        else:
            print("Back is clear")

        print("----------------------")

except KeyboardInterrupt:
    print("Stopping...")
    lidar.stop()
    lidar.disconnect()