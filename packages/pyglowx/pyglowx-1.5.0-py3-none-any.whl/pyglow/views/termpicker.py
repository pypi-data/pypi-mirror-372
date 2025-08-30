import sys
import os
from pyglow.styles.foreground import Fore
from pyglow.styles.style import Style
from pyglow.mapping import ANSI_RESET


IS_WINDOWS = os.name == "nt"

if IS_WINDOWS:
    import msvcrt
else:
    import tty
    import termios


def _get_key():
    if IS_WINDOWS:
        ch = msvcrt.getch()
        if ch == b"\xe0":
            ch2 = msvcrt.getch()
            return ch + ch2
        return ch
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch1 = sys.stdin.read(1)
            if ch1 == "\x1b":  # Escape sequence
                ch2 = sys.stdin.read(1)
                ch3 = sys.stdin.read(1)
                return ch1 + ch2 + ch3
            return ch1
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _clear_lines(n):
    for _ in range(n):
        sys.stdout.write("\x1b[1A")
        sys.stdout.write("\x1b[2K")
    sys.stdout.flush()


class TermPicker:
    def __init__(self,
                 items,
                 label="Select an item",
                 highlight_color=Fore.CYAN,
                 cursor_symbol=">"
                 ):
        self.items = items
        self.label = label
        self.highlight_color = highlight_color
        self.cursor_symbol = cursor_symbol
        self.idx = 0

    def _draw(self):
        _clear_lines(len(self.items))
        for i, item in enumerate(self.items):
            cursor = f"{self.cursor_symbol} " if i == self.idx else "  "
            if i == self.idx:
                print(f"{Style.BOLD}{self.highlight_color}{cursor}{item}{ANSI_RESET}")
            else:
                print(f"{cursor}{item}")

    def pick(self):
        print(self.label + "\n")
        for i, item in enumerate(self.items):
            cursor = f"{self.cursor_symbol} " if i == self.idx else "  "
            if i == self.idx:
                print(f"{Style.BOLD}{self.highlight_color}{cursor}{item}{ANSI_RESET}")
            else:
                print(f"{cursor}{item}")

        while True:
            key = _get_key()
            if (not IS_WINDOWS and key == "\x1b[A") or (IS_WINDOWS and key == b"\xe0H"):
                self.idx = (self.idx - 1) % len(self.items)
            elif (not IS_WINDOWS and key == "\x1b[B") or (IS_WINDOWS and key == b"\xe0P"):
                self.idx = (self.idx + 1) % len(self.items)
            elif key in ["\n", "\r", b"\r", b"\n"]:
                return self.items[self.idx]
            self._draw()
