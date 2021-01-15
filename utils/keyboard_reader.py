import sys
import termios
import tty


class KeyboardReader:
    def __init__(self, name=''):
        self.name = name

    def readChar(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        if ch == '0x03':
            raise KeyboardInterrupt
        return ch

    def readKey(self, getchar_fn=None):
        getchar = getchar_fn or self.readChar
        c1 = getchar()
        if ord(c1) != 0x1b:
            return c1
        c2 = getchar()
        if ord(c2) != 0x5b:
            return c1
        c3 = getchar()
        return ord(c3) - 65  # 0=Up, 1=Down, 2=Right, 3=Left arrows
