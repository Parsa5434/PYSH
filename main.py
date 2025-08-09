from time import sleep
from threading import Event, Timer, Thread
from gpiozero import DigitalInputDevice, MotionSensor, DigitalOutputDevice

# Setup GPIO devices
remoteA = DigitalInputDevice(23)  # Button 1 - arm button
remoteB = DigitalInputDevice(24)
remoteC = DigitalInputDevice(25)
remoteD = DigitalInputDevice(17)  # Button 4 - disarm button
humanSensor = MotionSensor(27)
siren = DigitalOutputDevice(22)

# Events for each pin
events = {
    "1": {"pin": remoteA, "event": Event()},
    "2": {"pin": remoteB, "event": Event()},
    "3": {"pin": remoteC, "event": Event()},
    "4": {"pin": remoteD, "event": Event()},
    "human_sensor": {"pin": humanSensor, "event": Event()},
}

armed = False  # Global state to track if system is armed

# Stop siren helper
def stop_siren_after(seconds):
    Timer(seconds, siren.off).start()

# Callback factory
def make_unpause(key):
    def callback():
        events[key]["event"].set()
    return callback

def arm_system():
    global armed
    if not armed:
        armed = True
        print("🔒 System armed.")
    else:
        print("System is already armed.")

def disarm_system():
    global armed
    if armed:
        armed = False
        siren.off()
        print("🔓 System disarmed. Siren off.")
    else:
        print("System is already disarmed.")

def use_siren(key):
    global armed
    if key == "human_sensor":
        if armed:
            print("Motion detected. Waiting 3 seconds to confirm...")
            sleep(3)
            if humanSensor.is_active:
                print("Motion still present. Triggering siren.")
                siren.on()
                stop_siren_after(100)
            else:
                print("False alarm. No motion after 3 seconds.")
        else:
            print("Motion detected but system is disarmed. Ignoring.")

    elif key == "1":
        arm_system()

    elif key == "4":
        disarm_system()

    else:
        print(f"Unhandled key '{key}' in use_siren.")

# Set up callbacks
for key, value in events.items():
    value["pin"].when_activated = make_unpause(key)

# Main loop
while True:
    for key, value in events.items():
        if value["event"].is_set():
            print(f"🎯 Event triggered: {key}")
            value["event"].clear()
            Thread(target=use_siren, args=(key,)).start()
    sleep(0.1)
