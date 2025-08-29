import sys
import time
import threading
import itertools
from functools import wraps
import asyncio

COLORS = [
    "\033[91m",  # red
    "\033[92m",  # green
    "\033[93m",  # yellow
    "\033[94m",  # blue
    "\033[95m",  # magenta
    "\033[96m",  # cyan
]
RESET = "\033[0m"


def with_animation(text="Processing"):
    """Decorator that shows a colorful spinner while a function runs (sync or async)."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            stop_event = threading.Event()
            spinner_cycle = itertools.cycle(["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"])
            color_cycle = itertools.cycle(COLORS)

            def spinner():
                while not stop_event.is_set():
                    color = next(color_cycle)
                    sys.stdout.write(f"\r{color}{text} {next(spinner_cycle)}{RESET}")
                    sys.stdout.flush()
                    time.sleep(0.1)

            t = threading.Thread(target=spinner)
            t.start()

            try:
                return await func(*args, **kwargs)
            finally:
                stop_event.set()
                t.join()
                # sys.stdout.write("\r✅ Done!                          \n")

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            stop_event = threading.Event()
            spinner_cycle = itertools.cycle(["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"])
            color_cycle = itertools.cycle(COLORS)

            def spinner():
                while not stop_event.is_set():
                    color = next(color_cycle)
                    sys.stdout.write(f"\r{color}{text} {next(spinner_cycle)}{RESET}")
                    sys.stdout.flush()
                    time.sleep(0.1)

            t = threading.Thread(target=spinner)
            t.start()

            try:
                return func(*args, **kwargs)
            finally:
                stop_event.set()
                t.join()
                #sys.stdout.write("\r✅ Done!                          \n")

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
