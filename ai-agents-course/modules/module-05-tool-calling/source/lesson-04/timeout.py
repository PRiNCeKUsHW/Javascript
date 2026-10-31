# timeout.py: never wait forever for a tool
import threading
import time


def run_with_timeout(func, seconds):
    result = []
    worker = threading.Thread(target=lambda: result.append(func()), daemon=True)
    worker.start()
    worker.join(seconds)             # wait at most `seconds`
    if worker.is_alive():
        return f"Error: timed out after {seconds} s"
    return result[0]


def quick_lookup():
    return "3 notes found"


def stuck_service():
    time.sleep(60)                   # a server that never answers
    return "too late"


start = time.monotonic()
print(run_with_timeout(quick_lookup, 2))
print(run_with_timeout(stuck_service, 2))
print(f"total wait: {time.monotonic() - start:.0f} s")
