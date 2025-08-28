class Cursor:
    up    = '\033[A'
    down  = '\033[B'
    right = '\033[C'
    left  = '\033[D'

    clear_line = '\033[2K'
    home       = '\033[G'

    @staticmethod
    def move_to(x: int, y: int) -> str:
        return f"\033[{y};{x}H"
