import os
import difflib
from pyglow.mapping import FOREGROUND_COLORS, BACKGROUND_COLORS, STYLES

def preprocess(tag: str) -> str:
    return tag.strip()

def is_terminal_supports_hyperlink() -> bool:
    if "WT_SESSION" in os.environ:
        return True
    if os.environ.get("TERM_PROGRAM") == "iTerm.app":
        return True
    term = os.environ.get("TERM", "").strip().lower()
    if any(x in term for x in ["xterm", "gnome", "vte", "kitty", "wezterm"]):
        return True
    return False


def get_closest_match(tag: str) -> str:
    all_mappings = list(FOREGROUND_COLORS.keys()) + list(BACKGROUND_COLORS.keys()) + list(STYLES.keys())
    matches = difflib.get_close_matches(preprocess(tag), all_mappings, n=3, cutoff=0.7)
    return matches[0] if matches else None
