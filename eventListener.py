import threading
import time
from blinker import signal

stop_signal = signal('stop')

def event_listener():
    while True:
        time.sleep(1)
        # Simulate receiving a stop event
        user_input = input("Type 'stop' to send stop signal: ").strip().lower()
        if user_input == 'stop':
            stop_signal.send(None)
