def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
    return r, g, b


def hex_to_foreground(hex_color):
    r, g, b = hex_to_rgb(hex_color)
    return f"\033[38;2;{r};{g};{b}m"


def hex_to_background(self, hex_color):
    r, g, b = self.hex_to_rgb(hex_color)
    return f"\033[48;2;{r};{g};{b}m"
