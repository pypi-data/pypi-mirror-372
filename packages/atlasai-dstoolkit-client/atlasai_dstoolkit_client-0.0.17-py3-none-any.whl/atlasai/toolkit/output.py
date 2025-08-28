from rich.console import Console
from rich.text import Text

console = Console()

def print_title(text):
    text = Text(text, style="bold underline", justify="center")
    console.print(text)

def print_subtitle(text):
    text = Text(text, style="italic cyan", justify="center")
    console.print(text)

def print_body(text):
    if isinstance(text, bytes):
        text = text.decode("utf-8")
    text = Text(text, style="white", justify="left")
    console.print(text)
