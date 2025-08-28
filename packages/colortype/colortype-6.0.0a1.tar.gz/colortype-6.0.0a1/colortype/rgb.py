def fore_rgb(r: int, g: int, b: int) -> str:
    """24-bit RGB foreground color"""
    return f"\033[38;2;{r};{g};{b}m"

def back_rgb(r: int, g: int, b: int) -> str:
    """24-bit RGB background color"""
    return f"\033[48;2;{r};{g};{b}m"
