import threading
import time
from roboty import Robot


class ActionRunner:

    def __init__(self):
        self.running = False
        self.robot = Robot()

        # Start robot in neutral position
        print("Centering robot")
        self.robot.center_all()


    def run_actions(self, actions):
        if not actions:
            return

        thread = threading.Thread(target=self._execute, args=(actions,))
        thread.start()


    def _execute(self, actions):
        self.running = True
        print("Executing actions:", actions)

        for action in actions:

            if not self.running:
                break

            print("Running:", action)

            # -------------------------
            # HEAD YES
            # -------------------------
            if action == "head_yes":
                self.robot.set_head_tilt(-0.6)
                time.sleep(.4)

                self.robot.set_head_tilt(0.6)
                time.sleep(.4)

                self.robot.set_head_tilt(0)

            # -------------------------
            # HEAD NO
            # -------------------------
            elif action == "head_no":
                self.robot.set_head_pan(-0.7)
                time.sleep(.4)

                self.robot.set_head_pan(0.7)
                time.sleep(.4)

                self.robot.set_head_pan(0)

            # -------------------------
            # DRIVE FORWARD
            # -------------------------
            elif action == "drive_forward":
                self.robot.driveFB(0.8)
                time.sleep(1)
                self.robot.driveFB(0)

            # -------------------------
            # DRIVE BACKWARD
            # -------------------------
            elif action == "drive_back":
                self.robot.driveFB(-0.8)
                time.sleep(1)
                self.robot.driveFB(0)

            # -------------------------
            # TURN LEFT
            # -------------------------
            elif action == "turn_left":
                self.robot.driveTr(-0.8)
                time.sleep(.8)
                self.robot.driveTr(0)

            # -------------------------
            # TURN RIGHT
            # -------------------------
            elif action == "turn_right":
                self.robot.driveTr(0.8)
                time.sleep(.8)
                self.robot.driveTr(0)   # FIX: added stop

            # -------------------------
            # DANCE 90
            # -------------------------
            elif action == "dance90":
                for i in range(3):

                    if not self.running:
                        break

                    self.robot.driveTr(0.5)
                    time.sleep(0.4)

                    self.robot.driveTr(0)
                    time.sleep(0.4)

                    self.robot.driveTr(-0.5)
                    time.sleep(0.4)

                    self.robot.driveTr(0)
                    time.sleep(0.4)

                self.robot.driveTr(0)

            # -------------------------
            # ARM RAISE
            # -------------------------
            elif action == "arm_raise":
                print("Raising right arm")

                self.robot.rsUD.set_speed(1)
                time.sleep(.4)

                self.robot.rwTW.set_speed(0.5)
                time.sleep(.8)

                self.robot.rwTW.set_speed(-0.5)
                time.sleep(.8)

                self.robot.rwTW.set_speed(0)
                time.sleep(0.4)

                self.robot.rsUD.set_speed(0)

            else:
                print("Unknown action:", action)

        self.running = False


    def stop_all(self):
        print("Stopping all actions.")
        self.running = False
        self.robot.stop_all()