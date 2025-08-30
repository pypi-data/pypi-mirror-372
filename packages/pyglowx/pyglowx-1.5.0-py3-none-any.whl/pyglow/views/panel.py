from pyglow.styles.border import Border
from pyglow.parser import ANSI_RESET
from pyglow.styles.style import Style
from pyglow.utilities.color_utils import hex_to_foreground

class Panel:
    BORDER_STYLES = {
        "rounded": {"tl": "╭", "tr": "╮", "bl": "╰", "br": "╯", "h": "─", "v": "│"},
        "square": {"tl": "┌", "tr": "┐", "bl": "└", "br": "┘", "h": "─", "v": "│"},
        "heavy": {"tl": "┏", "tr": "┓", "bl": "┗", "br": "┛", "h": "━", "v": "┃"},
        "double": {"tl": "╔", "tr": "╗", "bl": "╚", "br": "╝", "h": "═", "v": "║"},
        "minimal": {"tl": "+", "tr": "+", "bl": "+", "br": "+", "h": "-", "v": "|"}
    }

    def __init__(self,
                 title="",
                 subtitle="",
                 title_color="#FFFFFF",
                 subtitle_color="#FFFFFF",
                 border_color="#3F51B5",
                 border_style=Border.ROUNDED,
                 padding=1,
                 align="left"):
        self.title = title
        self.subtitle = str(subtitle) if subtitle else ""
        self.title_color = hex_to_foreground(title_color)
        self.text_color = hex_to_foreground(subtitle_color)
        self.border_color = hex_to_foreground(border_color)
        self.padding = padding
        self.align = align.lower()
        self.set_border_style(border_style)

    def set_title(self, title):
        self.title = title

    def set_subtitle(self, subtitle):
        self.subtitle = subtitle

    def set_border_style(self, style_name):
        style = self.BORDER_STYLES.get(style_name, self.BORDER_STYLES["rounded"])
        self.TOP_LEFT = style["tl"]
        self.TOP_RIGHT = style["tr"]
        self.BOTTOM_LEFT = style["bl"]
        self.BOTTOM_RIGHT = style["br"]
        self.H = style["h"]
        self.V = style["v"]

    def _align_text(self, line, content_width):
        if self.align == "center":
            return line.center(content_width)
        elif self.align == "right":
            return line.rjust(content_width)
        else:
            return line.ljust(content_width)

    def show(self):
        lines = self.subtitle.split("\n")
        content_width = max(len(line) for line in lines) if lines else 0
        title_width = len(self.title) if self.title else 0
        content_width = max(content_width, title_width)

        full_width = content_width + 2 * self.padding

        if self.title:
            title_str = f" {self.title} "
            extra_space = full_width - len(title_str)
            left_h = extra_space // 2
            right_h = extra_space - left_h
            top_line = (
                self.TOP_LEFT +
                self.H * left_h +
                f"{Style.BOLD}{self.title_color}{title_str}{ANSI_RESET}{self.border_color}" +
                self.H * right_h +
                self.TOP_RIGHT
            )
        else:
            top_line = self.TOP_LEFT + self.H * full_width + self.TOP_RIGHT

        print(f"{self.border_color}{top_line}{ANSI_RESET}")

        for line in lines:
            aligned_line = self._align_text(line, content_width)
            print(f"{self.border_color}{self.V}{' ' * self.padding}{self.text_color}{aligned_line}{ANSI_RESET}{self.border_color}{' ' * self.padding}{self.V}{ANSI_RESET}")

        bottom_line = self.BOTTOM_LEFT + self.H * full_width + self.BOTTOM_RIGHT
        print(f"{self.border_color}{bottom_line}{ANSI_RESET}")
