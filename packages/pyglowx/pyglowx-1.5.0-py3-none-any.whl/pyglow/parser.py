import re
from .mapping import (
    ANSI_RESET,
    contains_foreground_color,
    contains_background_color,
    contains_style,
    get_foreground_color,
    get_background_color,
    get_style,
)
from pyglow.utilities.utils import get_closest_match

rgb_pattern = re.compile(r"^rgb\((\d{1,3}),(\d{1,3}),(\d{1,3})\)$")
hex_pattern = re.compile(r"^hex\(#([A-Fa-f0-9]{6})\)$")


class PyGlowParser:
    @staticmethod
    def parse(input_str: str):
        output = []
        stack = []
        i = 0

        while i < len(input_str):
            if input_str.startswith("[/", i):
                end = input_str.find("]", i)
                if end == -1:
                    raise ValueError("Unclosed tag")
                if stack:
                    tag = stack.pop()
                    if tag["type"] == "link":
                        output.append("\033]8;;\033\\")
                    output.append(ANSI_RESET)
                    for s in stack:
                        if s["type"] == "style":
                            output.append(s["ansi"])
                i = end + 1
                continue
            elif input_str[i] == "[":
                end = input_str.find("]", i)
                if end == -1:
                    raise ValueError("Unclosed tag")
                tag_string = input_str[i + 1:end].strip()
                tag_lower = tag_string.lower()
                if tag_lower.startswith("link="):
                    url = tag_string[5:]
                    stack.append({"type": "link", "url": url})
                    output.append(f"\033]8;;{url}\033\\")
                    i = end + 1
                    continue
                tags = tag_string.split()
                ansi = []
                for tag in tags:
                    tag_lower = tag.lower()
                    rgb_match = rgb_pattern.match(tag_lower)
                    hex_match = hex_pattern.match(tag_lower)
                    if rgb_match:
                        r, g, b = map(int, rgb_match.groups())
                        ansi.append(f"\u001b[38;2;{r};{g};{b}m")
                    elif hex_match:
                        hex_code = hex_match.group(1)
                        r = int(hex_code[0:2], 16)
                        g = int(hex_code[2:4], 16)
                        b = int(hex_code[4:6], 16)
                        ansi.append(f"\u001b[38;2;{r};{g};{b}m")
                    elif contains_foreground_color(tag_lower):
                        ansi.append(get_foreground_color(tag_lower))
                    elif contains_background_color(tag_lower):
                        ansi.append(get_background_color(tag_lower))
                    elif contains_style(tag_lower):
                        ansi.append(get_style(tag_lower))
                    else:
                        suggestion = get_closest_match(tag_lower)
                        if suggestion:
                            raise KeyError(f"unknown tag: {tag}, did you mean '{suggestion}'?")
                        else:
                            raise KeyError(f"unknown tag: {tag}")
                if ansi:
                    ansi_str = "".join(ansi)
                    output.append(ansi_str)
                    stack.append({"type": "style", "ansi": ansi_str})
                i = end + 1
            else:
                output.append(input_str[i])
                i += 1
        while stack:
            tag = stack.pop()
            if tag["type"] == "link":
                output.append("\033]8;;\033\\")
            output.append(ANSI_RESET)
        return "".join(output)
