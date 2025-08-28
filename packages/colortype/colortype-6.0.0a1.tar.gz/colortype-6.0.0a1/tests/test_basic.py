from colortype import console

def test_console():
    out = console("[red]hello[reset]")
    assert "\033[31m" in out and "\033[0m" in out
