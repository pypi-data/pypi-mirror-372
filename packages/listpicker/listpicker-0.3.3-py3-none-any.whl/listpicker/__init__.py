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

"""
Interactive list selection with filtering.

    listpicker.pick("Choose pizza type:", ("Thin crust", …))
    listpicker.pick_multiple("Choose toppings:", ("Pepperoni", …))
"""

import sys
from typing import Optional, Sequence, TextIO

from .listpicker import ListPicker

__all__ = ("pick", "pick_multiple")


def pick(
    prompt: str,
    options: Sequence[str],
    *,
    force_prompt: bool = False,
    infile: TextIO = sys.stdin,
    outfile: TextIO = sys.stdout,
) -> Optional[str]:
    """
    Prompt user to choose one option from many. If "options" is empty, returns
    None without prompting. Similarly, if "options" has one element, that
    element is returned without prompting the user. Pass force_prompt=True to
    always prompt the user when len(options) == 1.
    """
    if len(options) == 0:
        return None

    if len(options) == 1 and not force_prompt:
        return options[0]

    if picks := ListPicker(prompt, options, infile=infile, outfile=outfile).pick():
        return picks[0]

    return None


def pick_multiple(
    prompt: str,
    options: Sequence[str],
    *,
    force_prompt: bool = False,
    minimum: int = 1,
    preselected: Optional[Sequence[str]] = None,
    infile: TextIO = sys.stdin,
    outfile: TextIO = sys.stdout,
) -> list[str]:
    """
    Prompt user to select a subset of "options". If len(options) <= minimum,
    the same options are returned in a new list without prompting the user.
    Pass force_prompt=True to always prompt the user when len(options) == minimum.

    Preselected options can be passed with the "preselected" keyword argument.

    This function always returns a new list that contains a subsequence of
    "options" (i.e. same ordering).
    """
    if len(options) < minimum or len(options) == minimum and not force_prompt:
        return list(options)

    return ListPicker(
        prompt,
        options,
        multiselect=True,
        minimum=minimum,
        preselected=preselected,
        infile=infile,
        outfile=outfile,
    ).pick()
