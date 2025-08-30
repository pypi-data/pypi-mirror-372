from .parser import PyGlowParser
from .mapping import ANSI_RESET


class Glow:

    @staticmethod
    def parse(text: str) -> str:
        return PyGlowParser.parse(text)

    @staticmethod
    def print(text: str):
        print(Glow.parse(text))

    @staticmethod
    def printc(text: str):
        print(f"{text}{ANSI_RESET}")

    @staticmethod
    def prints(text: str, style: str):
        Glow.print(f"[{style}]{text}[/]")
