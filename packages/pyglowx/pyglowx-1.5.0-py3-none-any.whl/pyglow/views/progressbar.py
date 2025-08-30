import sys
import shutil
from pyglow.parser import ANSI_RESET
from pyglow.utilities.color_utils import hex_to_foreground

class ProgressBar:
    blocks = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]

    def __init__(self,
                 total=100,
                 width=None,
                 color="#00FF00",
                 show_percent=True,
                 label=""):
        self.total = total
        self.color = hex_to_foreground(color)
        self.show_percent = show_percent
        self.current = 0
        self.label = label

        if width is None:
            term_width = shutil.get_terminal_size((80, 20)).columns
            self.width = term_width - len(label) - 8
        else:
            self.width = width

    def update(self, value):
        self.current = min(max(0, value), self.total)
        ratio = self.current / self.total
        total_blocks = self.width * 8  # 8 sub-blocks per cell
        filled = int(ratio * total_blocks)

        full = filled // 8
        remainder = filled % 8

        line = "█" * full
        if remainder > 0:
            line += self.blocks[remainder]

        percent = f"{int(ratio * 100)}%" if self.show_percent else ""
        space = " " * (self.width - len(line))

        sys.stdout.write(f"\r{self.label} {self.color}{line}{ANSI_RESET}{space} {percent}")
        sys.stdout.flush()

    def finish(self):
        self.update(self.total)
        print()
