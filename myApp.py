from flask import Flask, render_template, request, jsonify
from roboty import Robot
from sp import speak
from dialog_engine import DialogEngine
from action_runner import ActionRunner
from state_machine import StateMachine

#state_machine = StateMachine()
#action_runner = ActionRunner()
#dialog_engine = DialogEngine(state_machine, action_runner)


app = Flask(__name__)

state_machine = StateMachine()
action_runner = ActionRunner()
dialog_engine = DialogEngine(state_machine, action_runner, "testDialogFileForPractice.txt")

robot = Robot()

# Center robot safely at startup
robot.center_all()


@app.route("/")
def index():
    return render_template("index.html")


# -------------------------
# DRIVE (FB + TURN ports)
# -------------------------
@app.route("/drive", methods=["POST"])
def drive():
    data = request.json

    try:
        fb = float(data["fb"])
        tr = float(data["tr"])

        # Validate range
        if not (-1.0 <= fb <= 1.0 and -1.0 <= tr <= 1.0):
            return jsonify({"status": "error", "message": "Invalid range"}), 400

        robot.driveFB(fb)
        robot.driveTr(tr)

        return jsonify({"status": "ok"})

    except:
        return jsonify({"status": "error", "message": "Bad data"}), 400


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

    print("Incoming data:", data)  # DEBUG

    if not data or "value" not in data:
        return jsonify({"status": "error", "message": "No value received"}), 400

    try:
        value = int(data["value"])
    except:
        return jsonify({"status": "error", "message": "Invalid number"}), 400

    print("Parsed value:", value)  # DEBUG

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
