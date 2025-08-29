import signal
import threading


def wait_for_ctrl_c():
    stop_event = threading.Event()

    def handler(signum, frame):
        stop_event.set()

    signal.signal(signal.SIGINT, handler)
    stop_event.wait()
