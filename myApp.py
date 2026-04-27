from flask import Flask, render_template, request, jsonify
from roboty import Robot
from sp import speak
from dialog_engine import DialogEngine
from action_runner import ActionRunner
from state_machine import StateMachine
from adafruit_rplidar import RPLidar
import threading
import time


app = Flask(__name__)

state_machine = StateMachine()
action_runner = ActionRunner()
dialog_engine = DialogEngine(state_machine, action_runner, "testDialogFileForPractice.txt")

robot = Robot()

robot.center_all()


#Lidar
PORT_NAME = "/dev/ttyUSB0"
DIST_THRESHOLD = 1000  # mm

FRONT_MIN_ANGLE = 330
FRONT_MAX_ANGLE = 30

BACK_MIN_ANGLE = 150
BACK_MAX_ANGLE = 210


class Lidar:
    def __init__(self, port_name, dist_threshold=500):
        self.port_name = port_name
        self.dist_threshold = dist_threshold

        self.front_blocked = False
        self.back_blocked = False

        self.lidar = None
        self.running = False
        self.lock = threading.Lock()
        self.thread = None

    def start(self):
        try:
            self.lidar = RPLidar(None, self.port_name, timeout=3)
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            print("LiDAR safety monitor started.")
        except Exception as e:
            print(f"Failed to start LiDAR: {e}")

    def stop(self):
        self.running = False
        try:
            if self.lidar:
                self.lidar.stop()
                self.lidar.disconnect()
        except Exception as e:
            print(f"Error stopping LiDAR: {e}")

    def _monitor_loop(self):
        while self.running:
            try:
                for scan in self.lidar.iter_scans():
                    if not self.running:
                        break

                    front_blocked = False
                    back_blocked = False

                    for (_, angle, distance) in scan:
                        if distance <= 0:
                            continue

                        # Front zone: wraps around 360
                        if (angle >= FRONT_MIN_ANGLE) or (angle <= FRONT_MAX_ANGLE):
                            if distance < self.dist_threshold:
                                front_blocked = True

                        # Back zone
                        if BACK_MIN_ANGLE <= angle <= BACK_MAX_ANGLE:
                            if distance < self.dist_threshold:
                                back_blocked = True

                    with self.lock:
                        self.front_blocked = front_blocked
                        self.back_blocked = back_blocked

            except Exception as e:
                print(f"LiDAR read error: {e}")
                time.sleep(1)

    def get_state(self):
        with self.lock:
            return self.front_blocked, self.back_blocked


lidar_safety = Lidar(PORT_NAME, DIST_THRESHOLD)
lidar_safety.start()


@app.route("/")
def index():
    return render_template("index.html")


# drive forwards and backwards and turn ports
@app.route("/drive", methods=["POST"])
def drive():
    data = request.json

    try:
        fb = float(data["fb"])
        tr = float(data["tr"])

        if not (-1.0 <= fb <= 1.0 and -1.0 <= tr <= 1.0):
            return jsonify({"status": "error", "message": "Invalid range"}), 400

        front_blocked, back_blocked = lidar_safety.get_state()

        # Stop forward if front blocked
        if fb < 0 and front_blocked:
            robot.driveFB(0)
            robot.driveTr(0)
            return jsonify({
                "status": "blocked",
                "message": "Front blocked"
            })

        # Stop reverse if back blocked
        if fb > 0 and back_blocked:
            robot.driveFB(0)
            robot.driveTr(0)
            return jsonify({
                "status": "blocked",
                "message": "Back blocked"
            })

        robot.driveFB(fb)
        robot.driveTr(tr)

        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Bad data: {e}"}), 400


# -------------------------
# HEAD
# -------------------------
@app.route("/head", methods=["POST"])
def head():
    data = request.json

    try:
        tilt = float(data["tilt"])
        pan = float(data["pan"])

        if not (-1.0 <= tilt <= 1.0 and -1.0 <= pan <= 1.0):
            return jsonify({"status": "error"}), 400

        robot.set_head_tilt(tilt)
        robot.set_head_pan(pan)

        return jsonify({"status": "ok"})

    except:
        return jsonify({"status": "error"}), 400


# -------------------------
# WAIST
# -------------------------
@app.route("/waist", methods=["POST"])
def waist():
    data = request.json

    try:
        value = float(data["value"])

        if not (-1.0 <= value <= 1.0):
            return jsonify({"status": "error"}), 400

        robot.set_waist(value)

        return jsonify({"status": "ok"})

    except:
        return jsonify({"status": "error"}), 400


# -------------------------
# STOP
# -------------------------
@app.route("/stop", methods=["POST"])
def stop():
    robot.stop_all()
    return jsonify({"status": "stopped"})


@app.route("/say", methods=["POST"])
def say():
    data = request.get_json()

    print("Incoming data:", data)

    if not data or "value" not in data:
        return jsonify({"status": "error", "message": "No value received"}), 400

    try:
        value = int(data["value"])
    except:
        return jsonify({"status": "error", "message": "Invalid number"}), 400

    print("Parsed value:", value)

    if value not in [1, 2, 3, 4]:
        return jsonify({"status": "error", "message": "Out of range"}), 400

    speak(value)

    return jsonify({"status": "ok"})


@app.route("/dialog", methods=["POST"])
def dialog():
    data = request.get_json()
    user_text = data.get("input", "")

    dialog_engine.handle_input(user_text)

    return jsonify({"status": "ok"})


@app.route("/lidar_status", methods=["GET"])
def lidar_status():
    front_blocked, back_blocked = lidar_safety.get_state()
    return jsonify({
        "front_blocked": front_blocked,
        "back_blocked": back_blocked
    })


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    finally:
        lidar_safety.stop()
