import sys
import time
import shutil
import itertools
from pyglow.mapping import ANSI_RESET
from pyglow.utilities.color_utils import hex_to_foreground

class Spinner:

    def __init__(self, prefix="Loading", bar_color="#00FF00", delay=0.1):
        self.prefix = prefix
        self.bar_color = hex_to_foreground(bar_color)
        self.delay = delay
        self.spinner_cycle = itertools.cycle(["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"])
        self.running = False

    def start(self):
        self.running = True
        while self.running:
            sys.stdout.write(f"\r{self.bar_color}{next(self.spinner_cycle)}{ANSI_RESET} {self.prefix}")
            sys.stdout.flush()
            time.sleep(self.delay)

    def stop(self):
        self.running = False
        sys.stdout.write("\r" + " " * shutil.get_terminal_size((80, 20)).columns + "\r")
        sys.stdout.flush()
