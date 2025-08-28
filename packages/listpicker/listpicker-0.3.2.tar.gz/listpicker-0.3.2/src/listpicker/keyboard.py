# The MIT License (MIT)
#
# Copyright © 2024 Sung Pae <self@sungpae.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import termios
import tty
from typing import Optional, TextIO

import regex

from .util import bytes_to_int

# https://en.wikipedia.org/wiki/ANSI_escape_code#Terminal_input_sequences
NAMED_KEY_BY_CODE = {
    0: "Ctrl-Space",
    **{n + 1: f"Ctrl-{chr(ord('A') + n)}" for n in range(26)},
    0x7F: "Delete",
    bytes_to_int(0x1B, ord("["), ord("A")): "Up",
    bytes_to_int(0x1B, ord("["), ord("B")): "Down",
    bytes_to_int(0x1B, ord("["), ord("C")): "Right",
    bytes_to_int(0x1B, ord("["), ord("D")): "Left",
    bytes_to_int(0x1B, ord("["), ord("F")): "End",  # xterm
    bytes_to_int(0x1B, ord("["), ord("H")): "Home",  # xterm
    bytes_to_int(0x1B, ord("["), ord("1"), ord("~")): "Home",  # vt
    bytes_to_int(0x1B, ord("["), ord("4"), ord("~")): "End",  # vt
    bytes_to_int(0x1B, ord("["), ord("5"), ord("~")): "PageUp",  # vt
    bytes_to_int(0x1B, ord("["), ord("6"), ord("~")): "PageDown",  # vt
    bytes_to_int(0x1B, ord("["), ord("7"), ord("~")): "Home",  # vt
    bytes_to_int(0x1B, ord("["), ord("8"), ord("~")): "End",  # vt
    bytes_to_int(0x1B, ord("["), ord("1"), ord("1"), ord("~")): "F1",
    bytes_to_int(0x1B, ord("O"), ord("P")): "F1",
}


class NonCanonicalModeTerminalInput:
    def __init__(self, file: TextIO):
        if not file.isatty():
            raise ValueError(f"file is not a tty: ${file!r}")

        self._file = file

    def __enter__(self) -> TextIO:
        fd = self._file.fileno()
        self._old_attrs = termios.tcgetattr(fd)
        tty.setcbreak(fd, termios.TCSAFLUSH)
        return self._file

    def __exit__(self, *_args: object) -> None:
        termios.tcsetattr(self._file.fileno(), termios.TCSAFLUSH, self._old_attrs)
        self._old_attrs.clear()


def getkey(file: TextIO) -> Optional[str]:
    with NonCanonicalModeTerminalInput(file) as f:
        ch = f.read(1)

        if ch == "\x1b":
            ch = f.read(1)

            if ch in ("[", "O"):
                # The subset of escape sequences we accept end in a capital letter or tilde
                n = (0x1B << 8) | ord(ch)

                for _ in range(3):
                    ch = f.read(1)
                    n = (n << 8) | ord(ch)
                    if regex.fullmatch(r"[A-Z~]", ch):
                        break

                return NAMED_KEY_BY_CODE.get(n)

            # Ignore other escape sequences
            return None

        return NAMED_KEY_BY_CODE.get(ord(ch), ch)
