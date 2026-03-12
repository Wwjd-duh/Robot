import maestro
import time
import pyttsx3
# -------------------------
# Generic Servo / Motor
# -------------------------
class Motor:
    def __init__(self, controller, port, center=6000, range_=2000):
        self.controller = controller
        self.port = port
        self.center = center
        self.range_ = range_

    def set_speed(self, speed):
        """
        speed: -1.0 to 1.0
        """
        speed = max(-1.0, min(1.0, speed))
        target = int(self.center + speed * self.range_)
        self.controller.setTarget(self.port, target)

    def stop(self):
        self.controller.setTarget(self.port, self.center)

    def center_servo(self):
        """Move servo to its neutral center position."""
        self.controller.setTarget(self.port, self.center)


# -------------------------
# Robot Control Layer
# -------------------------
class Robot:
    def __init__(self):

        self.controller = maestro.Controller()

        # DRIVE
        self.FB_wheel = Motor(self.controller, 0)
        self.Turn_wheel = Motor(self.controller, 1)

        # HEAD
        self.head_tilt = Motor(self.controller, 3, center=6000, range_=2000)
        self.head_pan = Motor(self.controller, 4, center=6000, range_=3000)

        # WAIST
        self.waist = Motor(self.controller, 2, center=5000, range_=2000)

        # RIGHT ARM
        self.rsUD = Motor(self.controller, 5, center=5000, range_=1000)
        self.reSS = Motor(self.controller, 6, center=6000, range_=1000)
        self.reUD = Motor(self.controller, 7, center=5000, range_=1000)
        self.rwUD = Motor(self.controller, 8, center=6000, range_=1000)
        self.rwTW = Motor(self.controller, 9, center=6000, range_=2000)
        self.rwCL = Motor(self.controller, 10, center=6000, range_=1000)

        # LEFT ARM
        self.lsUD = Motor(self.controller, 11, center=5000, range_=1000)
        self.leSS = Motor(self.controller, 12, center=6000, range_=1000)
        self.leUD = Motor(self.controller, 13, center=5000, range_=1000)
        self.lwUD = Motor(self.controller, 14, center=6000, range_=1000)
        self.lwTW = Motor(self.controller, 15, center=6000, range_=2000)
        self.lwCL = Motor(self.controller, 16, center=5000, range_=1000)

        # Store all motors in a list (VERY useful)
        self.all_motors = [
            self.FB_wheel, self.Turn_wheel,
            self.head_tilt, self.head_pan,
            self.waist,
            self.rsUD, self.reSS, self.reUD,
            self.rwUD, self.rwTW, self.rwCL,
            self.lsUD, self.leSS, self.leUD,
            self.lwUD, self.lwTW, self.lwCL
        ]

    # -------------------------
    # CENTER ALL SERVOS
    # -------------------------
    def center_all(self):
        """Move every servo to neutral center."""
        for motor in self.all_motors:
            motor.center_servo()

    # -------------------------
    # DRIVE
    # -------------------------
    def driveFB(self, value):
        self.FB_wheel.set_speed(value)

    def driveTr(self, value):
        self.Turn_wheel.set_speed(value)

    # -------------------------
    # HEAD
    # -------------------------
    def set_head_tilt(self, value):
        self.head_tilt.set_speed(value)

    def set_head_pan(self, value):
        self.head_pan.set_speed(value)

    # -------------------------
    # WAIST
    # -------------------------
    def set_waist(self, value):
        self.waist.set_speed(value)

    # -------------------------
    # STOP EVERYTHING
    # -------------------------
    def stop_all(self):
        for motor in self.all_motors:
            motor.stop()
