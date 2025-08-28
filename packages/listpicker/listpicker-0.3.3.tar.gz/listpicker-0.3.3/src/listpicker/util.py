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

import regex

CSI_SGR_REGEX = regex.compile("\x1b\\[[\\d;]*m")
CSI_SGR_RESET_REGEX = regex.compile(
    r"""
    \x1b\[
    (?:
        0*                  # Empty or just zeros: m, 0m, 00m
        |
        [0-9;]*             # Any SGR codes...
        (?:
            (?<!            # NOT preceded by:
                \b(?:3|4|5|10)[89];2;[0-9]+;[0-9]+  # RGB format: 38;2;R;G where the following ;0 would be
                                                    # the blue component, not a reset
                |
                \b(?:3|4|5|10)[89];5                # 256-color format: 38;5 where the following ;0 would be
                                                    # the color index, not a reset
            )
            ;0+             # ...ending with ;0, ;00, etc.
            |
            ;+              # Or just semicolons: ;m, ;;m
        )
    )m
    """,
    regex.VERBOSE,
)
CSI_SGR_RESET = "\x1b[m"


def sgr_len(s: str) -> int:
    return len(CSI_SGR_REGEX.sub("", s))


def sgr_truncate(s: str, n: int) -> str:
    """
    Truncate string s to n non-SGR escape characters. O(n) worst-case performance.
    """
    if n >= len(s):
        return s

    dst = []
    cur_len = 0
    next_len = 0
    prev_stop = 0

    for m in CSI_SGR_REGEX.finditer(s):
        cur_start, cur_stop = m.span()
        next_len += cur_start - prev_stop

        if next_len >= n:
            dst.append(s[prev_stop : prev_stop + n - cur_len])
            dst.append(m.group(0) + CSI_SGR_RESET)
            return "".join(dst)

        dst.append(s[prev_stop:cur_start])
        dst.append(m.group(0))
        cur_len = next_len
        prev_stop = cur_stop

    dst.append(s[prev_stop : prev_stop + n - cur_len])

    if prev_stop:
        # We found at least one SGR escape, so SGR reset in case we are
        # truncating in the middle of an SGR pair.
        dst.append(CSI_SGR_RESET)

    return "".join(dst)


def plural_s(n: int, s: str = "s") -> str:
    "Pluralization helper"
    return "" if n == 1 else s


def smartcase_substring_match(substring: str, string: str) -> bool:
    # Disable case insensitivity when substring has an uppercase letter
    if regex.search(r"\p{Lu}", substring):
        return substring in string

    return substring in string.lower()


def bytes_to_int(*bs: int) -> int:
    "Parse a sequence of bytes as an integer"
    n = 0
    for b in bs:
        assert 0 <= b <= 255
        n <<= 8
        n |= b
    return n
