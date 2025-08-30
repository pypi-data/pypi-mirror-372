from pyglow.parser import ANSI_RESET
from pyglow.styles.style import Style
from pyglow.utilities.color_utils import hex_to_foreground

class Table:
    TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT = "┏", "┓", "┗", "┛"
    H, V = "━", "┃"
    TOP, BOTTOM, LEFT, RIGHT, CENTER = "┳", "┻", "┣", "┫", "╋"

    def __init__(self,
                 title=None,
                 title_color="#FFFFFF",
                 border_color="#3F51B5",
                 header_color="#2196F3",
                 row_colors=None):
        self.title = title
        self.title_color = hex_to_foreground(title_color)
        self.border_color = hex_to_foreground(border_color)
        self.header_color = hex_to_foreground(header_color)

        if row_colors:
            self.row_colors = [hex_to_foreground(c) for c in row_colors]
        else:
            self.row_colors = [hex_to_foreground("#795548")]

        self.columns = []
        self.rows = []

    def set_title(self, title):
        self.title = title

    def add_column(self, name):
        self.columns.append(str(name))

    def add_row(self, row):
        row = [str(cell) for cell in row]
        extra_cols = len(row) - len(self.columns)
        if extra_cols > 0:
            for i in range(extra_cols):
                self.columns.append(f"Column {len(self.columns) + 1}")
        self.rows.append(row)

    def _get_col_widths(self):
        all_rows = [self.columns] + self.rows
        return [max(len(str(row[i])) if i < len(row) else 0 for row in all_rows) for i in range(len(self.columns))]

    def _print_border(self, left, mid, right):
        widths = self._get_col_widths()
        line = left
        for i, w in enumerate(widths):
            line += self.H * (w + 2)
            line += mid if i < len(widths) - 1 else right
        print(f"{self.border_color}{line}{ANSI_RESET}")

    def _print_row(self, row, color=None, bold=False):
        widths = self._get_col_widths()
        line = self.border_color + self.V
        for i in range(len(widths)):
            cell = row[i] if i < len(row) else ""
            content = f"{cell:<{widths[i]}}"
            if bold:
                content = Style.BOLD + content
            cell_color = color or self.border_color
            line += f" {cell_color}{content}{self.border_color} {self.V}"
        line += ANSI_RESET
        print(line)

    def _print_title(self):
        if self.title:
            widths = self._get_col_widths()
            total_width = sum(widths) + 3 * len(widths) - 1
            print(f"{Style.BOLD}{self.title_color}{self.title.center(total_width)}{ANSI_RESET}")

    def show(self):
        self._print_title()
        self._print_border(self.TOP_LEFT, self.TOP, self.TOP_RIGHT)
        self._print_row(self.columns, color=self.header_color, bold=True)
        self._print_border(self.LEFT, self.CENTER, self.RIGHT)
        for i, row in enumerate(self.rows):
            color = self.row_colors[i % len(self.row_colors)]
            self._print_row(row, color=color)
        self._print_border(self.BOTTOM_LEFT, self.BOTTOM, self.BOTTOM_RIGHT)
