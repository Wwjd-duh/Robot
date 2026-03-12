const base = document.getElementById("joystick-base");
const stick = document.getElementById("joystick-stick");

let dragging = false;
const maxDistance = 70;

function sendDrive(fb, tr) {
    fetch("/drive", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({fb: fb, tr: tr})
    });
}

function stopRobot() {
    fetch("/stop", { method: "POST" });
}

function sendHead() {
    const tilt = document.getElementById("tilt").value;
    const pan = document.getElementById("pan").value;

    fetch("/head", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({tilt: tilt, pan: pan})
    });
}

function sendWaist() {
    const value = document.getElementById("waist").value;

    fetch("/waist", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({value: value})
    });
}

function handleMove(clientX, clientY) {
    const rect = base.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    let dx = clientX - centerX;
    let dy = clientY - centerY;

    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance > maxDistance) {
        dx = dx * maxDistance / distance;
        dy = dy * maxDistance / distance;
    }

    stick.style.left = (70 + dx) + "px";
    stick.style.top = (70 + dy) + "px";

    const x = dx / maxDistance;
    const y = dy / maxDistance;

    const fb = -y;   // forward/back
    const tr = x;    // turning

    sendDrive(fb, tr);
}

function resetStick() {
    stick.style.left = "70px";
    stick.style.top = "70px";
    stopRobot();
}

base.addEventListener("mousedown", () => dragging = true);
document.addEventListener("mouseup", () => {
    dragging = false;
    resetStick();
});

document.addEventListener("mousemove", (e) => {
    if (dragging) handleMove(e.clientX, e.clientY);
});

base.addEventListener("touchstart", () => dragging = true);
document.addEventListener("touchend", () => {
    dragging = false;
    resetStick();
});

document.addEventListener("touchmove", (e) => {
    if (dragging) {
        const touch = e.touches[0];
        handleMove(touch.clientX, touch.clientY);
    }
});
function sendSay(value) {
    fetch("/say", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ value: value })
    });
}


// Stop robot if page refreshes or closes
window.addEventListener("beforeunload", function () {
    navigator.sendBeacon("/stop");
});
