import re
from .fore import Fore
from .back import Back
from .style import Style

def console(text: str) -> str:
    """replace tags like [red], [b_blue], [bold] with ansi codes"""
    replacements = {
        # fore
        "[red]": Fore.red,
        "[green]": Fore.green,
        "[blue]": Fore.blue,
        "[yellow]": Fore.yellow,
        "[purple]": Fore.purple,
        "[cyan]": Fore.cyan,
        "[white]": Fore.white,
        "[black]": Fore.black,
        "[light_red]": Fore.light_red,
        "[light_green]": Fore.light_green,
        "[light_blue]": Fore.light_blue,
        "[light_yellow]": Fore.light_yellow,
        "[light_magenta]": Fore.light_magenta,
        "[light_cyan]": Fore.light_cyan,
        "[light_white]": Fore.light_white,

        # back
        "[b_red]": Back.red,
        "[b_blue]": Back.blue,
        "[b_green]": Back.green,
        "[b_yellow]": Back.yellow,
        "[b_white]": Back.white,
        "[b_black]": Back.black,

        # style
        "[bold]": Style.bold,
        "[dim]": Style.dim,
        "[underline]": Style.underline,
        "[reverse]": Style.reverse,
        "[blink]": Style.blink,
        "[reset]": Style.reset,
    }

    pattern = re.compile("|".join(map(re.escape, replacements.keys())))
    return pattern.sub(lambda m: replacements[m.group(0)], text)
