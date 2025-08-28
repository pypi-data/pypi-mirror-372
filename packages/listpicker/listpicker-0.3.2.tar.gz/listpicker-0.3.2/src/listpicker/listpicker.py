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

import dataclasses
import os
import signal
import sys
from enum import Enum, auto
from typing import Any, Optional, Sequence, TextIO

from . import keyboard, util

UI_KEY_NAMES = {
    " ": "Space",
    "Delete": "Backspace",
}


class Action(Enum):
    UP = auto()
    DOWN = auto()
    PAGE_UP = auto()
    PAGE_DOWN = auto()
    TOP = auto()
    BOTTOM = auto()
    HELP = auto()
    FILTER = auto()
    ERASE = auto()
    ERASE_LINE = auto()
    TOGGLE = auto()
    TOGGLE_ALL = auto()
    ACCEPT = auto()
    SUBMIT = auto()
    CANCEL = auto()


ACTION_KEYS = {
    Action.UP: ("Up", "k", "Ctrl-P"),
    Action.DOWN: ("Down", "j", "Ctrl-N"),
    Action.PAGE_UP: ("PageUp", "Ctrl-B"),
    Action.PAGE_DOWN: ("PageDown", "Ctrl-F"),
    Action.TOP: ("Home", "g", "Ctrl-A"),
    Action.BOTTOM: ("End", "G", "Ctrl-E"),
    Action.HELP: ("F1", "h", "H", "?"),
    Action.FILTER: ("F", "f", "l", "L"),
    Action.ERASE: ("Delete", "Ctrl-H"),
    Action.ERASE_LINE: ("Ctrl-W", "Ctrl-U"),
    Action.TOGGLE: (" ", "t"),
    Action.TOGGLE_ALL: ("Ctrl-A", "T"),
    Action.ACCEPT: ("Enter", "Ctrl-M", "Ctrl-J"),
    Action.SUBMIT: ("Ctrl-D",),
    Action.CANCEL: ("Ctrl-C", "Q", "q"),
}

ACTION_BY_KEY = {key: action for action, keys in ACTION_KEYS.items() for key in keys}

# https://en.wikipedia.org/wiki/ANSI_escape_code#CSI_(Control_Sequence_Introducer)_sequences
CSI_CURSOR_MOVE_UP = "\x1b[%dA"
CSI_CURSOR_MOVE_DOWN = "\x1b[%dB"
CSI_CURSOR_MOVE_FORWARD = "\x1b[%dC"
CSI_CURSOR_MOVE_BACK = "\x1b[%dD"
CSI_CURSOR_SET_POSITION = "\x1b[%d;%dH"
CSI_CLEAR_TO_BOTTOM = "\x1b[0J"
CSI_CLEAR_SCREEN = "\x1b[2J"
CSI_CURSOR_SHOW = "\x1b[?25h"
CSI_CURSOR_HIDE = "\x1b[?25l"
CSI_SGR = "\x1b[%sm%s\x1b[m"

SGR_STATUS = "36"  # cyan
SGR_MULTISELECT = "32"  # green
SGR_HELP = "3;33"  # italic;yellow
SGR_WARNING = "1;35"  # bold;magenta
SGR_FILTER_PROMPT = "32"  # green
SGR_CURRENT_SELECTION = "1;32"  # bold;green
SGR_CHECKED_OPTION = "36"  # cyan

OPTION_SUMMARY = CSI_SGR % (SGR_STATUS, "(Showing %s of %d) ")
MULTISELECT_SUMMARY = CSI_SGR % (SGR_MULTISELECT, "[☑ %d] ")
HELP_SUMMARY = CSI_SGR % (SGR_HELP, "(filter with f, submit with Enter, F1 for keybindings)")
HELP_MULTISELECT_SUMMARY = CSI_SGR % (SGR_HELP, "(filter with f, toggle with Space, F1 for keybindings)")
HELP_ACTIVE_FILTER_SUMMARY = CSI_SGR % (SGR_HELP, "(clear filter with Backspace, F1 for keybindings)")
HELP_ANYKEY = "(press any key to continue)"
FILTER_PROMPT = CSI_SGR % (SGR_FILTER_PROMPT, "Filter: %s")
FILTER_PROMPT_HELP = CSI_SGR % (SGR_HELP, "(Enter to accept, Ctrl-C to cancel)")
MINIMUM_MULTISELECT_WARNING = f"\nAt least {CSI_SGR % (SGR_WARNING, '%d')} selection%s required\n"
CONFIRMATION_PROMPT = f"Accept {CSI_SGR % (SGR_CURRENT_SELECTION, '%d')} selection%s? [Y/n]"
CONFIRMATION_PROMPT_HELP = "(press y or Enter to continue, any other key to return)"

PHI = (1 + 5**0.5) / 2
PANEL_WIDTH_PCT = PHI - 1  # ᵠ⁻¹
TOP_MARGIN_PCT = 2 - PHI  # 1 - ᵠ⁻¹


class ListPickerState(Enum):
    CANCELLED = auto()
    INACTIVE = auto()
    ACTIVE = auto()
    FILTERING = auto()
    HELP = auto()
    INFO = auto()
    CONFIRMATION = auto()


@dataclasses.dataclass(frozen=True)
class Option:
    number: int
    value: str

    def __post_init__(self) -> None:
        if "\n" in self.value:
            raise ValueError(f"Option value must not contain a newline: ${self.value}")

    def format(self, number_width: int, *, checked: Optional[bool]) -> str:
        checkbox: str

        match checked:
            case True:
                checkbox = "☑ "
            case False:
                checkbox = "☐ "
            case None:
                checkbox = ""

        return f"%-{number_width}s %s%s" % (str(self.number) + ".", checkbox, self.value)


class ListPicker:
    def __init__(
        self,
        prompt: str,
        options: Sequence[str],
        *,
        multiselect: bool = False,
        minimum: int = 0,
        preselected: Optional[Sequence[str]] = None,
        infile: TextIO = sys.stdin,
        outfile: TextIO = sys.stdout,
    ):
        self._prompt = prompt.rstrip("\n").split("\n")
        self._all_options = [Option(i + 1, o) for i, o in enumerate(options)]
        self._options = self._all_options
        self._option_index_width = len("%d." % (self._all_options[-1].number))
        self._multiselect = multiselect
        self._multiselect_minimum = minimum
        self._infile = infile
        self._outfile = outfile
        self._selected_options: set[Option] = set()
        self._preselected_options = set(preselected) if preselected else set()
        self._option_window = range(len(self._all_options))
        self._filter = ""
        self._columns = 80
        self._lines = 24
        self._state = ListPickerState.INACTIVE
        self._index = 0  # Array index of _options, not Option.number
        self._draw_height = 0
        self._max_draw_height = 0

        if self._multiselect_minimum > 0:
            if not self._multiselect:
                raise ValueError("minimum > 0 has no effect unless multiselect=True")
            if len(self._all_options) < self._multiselect_minimum:
                raise ValueError("not enough options to satisfy minimum constraint")

        if self._preselected_options:
            if not self._multiselect:
                raise ValueError("preselected options require multiselect=True")

            if invalid_options := self._preselected_options - set(options):
                raise ValueError(f"unknown preselected options: {invalid_options!r}")

    @property
    def _header_height(self) -> int:
        return len(self._prompt) + 1  # Plus one for filter bar

    def _clear_buffer_commands(self) -> str:
        return "\r" + (CSI_CURSOR_MOVE_UP % self._draw_height) + CSI_CLEAR_TO_BOTTOM

    def _write_screen(self, s: str) -> None:
        self._outfile.write(s)
        self._outfile.flush()  # Do not assume underlying file is write_through

    def _set_draw_height(self, n: int) -> None:
        self._max_draw_height = max(self._max_draw_height, n)
        self._draw_height = n

    def _update_option_window(self) -> None:
        # Resize window from bottom
        start = self._option_window.start
        stop = start + self._lines - 1 - self._header_height

        # Slide window to meet current index
        if self._index < start:
            stop -= start - self._index
            start = self._index
        elif self._index > stop:
            start += self._index - stop
            stop = self._index

        self._option_window = range(start, stop + 1)

    def _windowed_options(self) -> list[Option]:
        return self._options[self._option_window.start : self._option_window.stop]

    def _option_summary(self) -> str:
        if self._option_window.start == 0 and self._option_window.stop >= len(self._options):
            return ""

        if self._filter:
            return OPTION_SUMMARY % (len(self._windowed_options()), len(self._options))

        option_range = "%s-%s" % (
            self._option_window.start + 1,
            min(self._option_window.stop, len(self._all_options)),
        )

        return OPTION_SUMMARY % (option_range, len(self._options))

    def _build_panel(self, content: Sequence[str]) -> str:
        content_width = max((util.sgr_len(line) for line in content))
        panel_width = content_width + 4
        lines = ["┌" + "─" * (content_width + 2) + "┐"]
        lines.extend(f"│ %-{content_width + len(line) - util.sgr_len(line)}s │" % line for line in content)
        lines.append("└" + "─" * (content_width + 2) + "┘")

        # Truncate to fit viewport
        lines = lines[: self._lines]
        for i, line in enumerate(lines):
            lines[i] = util.sgr_truncate(line, self._columns) + ("\r\n" if i < len(lines) - 1 else "")

        # Place panel over text
        top_margin = "\n" * round((self._max_draw_height - len(lines)) * TOP_MARGIN_PCT)
        indent = (self._columns - panel_width) // 2
        left_margin = (CSI_CURSOR_MOVE_FORWARD % indent) if indent > 0 else ""
        return top_margin + left_margin + left_margin.join(lines)

    def _help_panel(self) -> str:
        keys = [a.name for a in Action]
        vals = [", ".join([UI_KEY_NAMES.get(k, k) for k in ACTION_KEYS[a]]) for a in Action]
        max_klen = max([len(k) for k in keys])
        max_vlen = max([len(v) for v in vals])
        max_width = max(max_klen + max_vlen + 3, len(HELP_ANYKEY))

        lines = [f"%-{max_klen}s │ %-{max_vlen}s" % (k, v) for k, v in zip(keys, vals, strict=False)]
        lines.append("")
        lines.append(CSI_SGR % (SGR_HELP, HELP_ANYKEY.center(max_width)))

        return self._build_panel(lines)

    def _info_panel(self, msg: str) -> str:
        return self._build_panel(msg.split("\n"))

    def _confirmation_panel(self) -> str:
        lines = [CONFIRMATION_PROMPT % (len(self._selected_options), util.plural_s(len(self._selected_options)))]
        lines.append("")

        other_linecount = 7
        max_height = min(len(self._option_window) + other_linecount, self._lines)
        max_width = max(
            round(self._columns * PANEL_WIDTH_PCT),
            util.sgr_len(CONFIRMATION_PROMPT),
            util.sgr_len(CONFIRMATION_PROMPT_HELP),
        )
        selection_count = max(0, max_height - other_linecount)
        selections = [o for o in self._all_options if o in self._selected_options][:selection_count]

        for option in selections:
            line = option.format(self._option_index_width, checked=True)
            if len(line) > max_width:
                line = line[: max_width - 1] + "…"
            lines.append(line)

        if hidden := len(self._selected_options) - len(selections):
            lines.append("… %d more" % hidden)

        lines.append("")
        lines.append(CSI_SGR % (SGR_HELP, CONFIRMATION_PROMPT_HELP.center(max(util.sgr_len(line) for line in lines))))

        return self._build_panel(lines)

    def _draw_panel(self, panel: str) -> None:
        self._write_screen("\r" + (CSI_CURSOR_MOVE_UP % self._draw_height) + panel)
        self._set_draw_height(panel.count("\n"))

    def _draw(self) -> None:
        out = [self._clear_buffer_commands()]

        self._update_option_window()

        # Prompt
        for i, line in enumerate(self._prompt):
            out.append(("\r\n" if i > 0 else "") + line[: self._columns])

        # Status bar
        status_bar = ["  "]

        if self._multiselect:
            status_bar.append(MULTISELECT_SUMMARY % len(self._selected_options))

        if self._state == ListPickerState.FILTERING:
            status_bar.append(FILTER_PROMPT % (self._filter + "_"))
            if not self._filter:
                status_bar.append(" " + FILTER_PROMPT_HELP)
        elif self._filter:
            status_bar.append(FILTER_PROMPT % self._filter)
            status_bar.append(" %s%s" % (self._option_summary(), HELP_ACTIVE_FILTER_SUMMARY))
        elif self._multiselect:
            status_bar.append(self._option_summary() + HELP_MULTISELECT_SUMMARY)
        else:
            status_bar.append(self._option_summary() + HELP_SUMMARY)

        out.append("\r\n" + util.sgr_truncate("".join(status_bar), self._columns))

        # Options list
        for i, option in enumerate(self._windowed_options()):
            out.append("\r\n")
            i += self._option_window.start
            checked = option in self._selected_options if self._multiselect else None

            if i == self._index:
                line = "> " + option.format(self._option_index_width, checked=checked)
                # Replace all SGR resets in this line with SGR_CURRENT_SELECTION style so
                # that SGR sequences within the string do not reset our style.
                line = util.CSI_SGR_RESET_REGEX.sub(f"\x1b[{SGR_CURRENT_SELECTION}m", line)
                out.append(CSI_SGR % (SGR_CURRENT_SELECTION, line[: self._columns]))
            else:
                line = "  " + option.format(self._option_index_width, checked=checked)
                if checked:
                    out.append(CSI_SGR % (SGR_CHECKED_OPTION, line[: self._columns]))
                else:
                    out.append(line[: self._columns])

        buf = "".join(out)
        self._write_screen(buf)
        self._set_draw_height(buf.count("\n"))

        match self._state:
            case ListPickerState.HELP:
                self._draw_panel(self._help_panel())
            case ListPickerState.INFO:
                self._draw_panel(self._info_panel(self._info_message))
            case ListPickerState.CONFIRMATION:
                self._draw_panel(self._confirmation_panel())

    def _sigwinch_handler(self, _signum: Any, _frame: Any) -> None:
        self._columns, self._lines = os.get_terminal_size(self._outfile.fileno())
        self._write_screen(CSI_CLEAR_SCREEN + CSI_CURSOR_SET_POSITION % (1, 1))
        self._max_draw_height = 0
        self._draw()

    def _set_filter(self, filter_str: str) -> None:
        current_option_number = self._options[self._index].number if self._options else 0
        self._filter = filter_str

        if filter_str:
            self._options = [o for o in self._all_options if util.smartcase_substring_match(filter_str, o.value)]
        else:
            self._options = self._all_options

        self._index = next((i for i, o in enumerate(self._options) if o.number >= current_option_number), 0)

    def _toggle_option(self, option: Option) -> None:
        if option in self._selected_options:
            self._selected_options.remove(option)
        else:
            self._selected_options.add(option)

    def _handle_main_input(self, key: str) -> ListPickerState:
        match ACTION_BY_KEY.get(key):
            case Action.UP:
                self._index = max(self._index - 1, 0)
            case Action.DOWN:
                self._index = min(self._index + 1, max(len(self._options) - 1, 0))
            case Action.PAGE_UP:
                self._index = max(self._index - round(len(self._option_window) / 2) + 1, 0)
            case Action.PAGE_DOWN:
                self._index = min(self._index + round(len(self._option_window) / 2) - 1, max(len(self._options) - 1, 0))
            case Action.TOP:
                self._index = 0
            case Action.BOTTOM:
                self._index = len(self._options) - 1
            case Action.HELP:
                return ListPickerState.HELP
            case Action.FILTER:
                return ListPickerState.FILTERING
            case Action.ERASE | Action.ERASE_LINE:
                self._set_filter("")
            case Action.TOGGLE:
                if self._multiselect and self._index < len(self._options):
                    self._toggle_option(self._options[self._index])
            case Action.TOGGLE_ALL:
                current_options = set(self._options)
                if current_options.issubset(self._selected_options):
                    self._selected_options -= current_options
                else:
                    self._selected_options |= current_options
            case Action.ACCEPT:
                if self._multiselect:
                    if len(self._selected_options) < self._multiselect_minimum:
                        self._info_message = MINIMUM_MULTISELECT_WARNING % (
                            self._multiselect_minimum,
                            util.plural_s(self._multiselect_minimum),
                        )
                        return ListPickerState.INFO
                    return ListPickerState.CONFIRMATION

                if self._index < len(self._options):
                    self._toggle_option(self._options[self._index])
                    return ListPickerState.INACTIVE
            case Action.SUBMIT:
                if not self._multiselect:
                    self._selected_options.add(self._options[self._index])
                return ListPickerState.INACTIVE
            case Action.CANCEL:
                self._selected_options.clear()
                return ListPickerState.CANCELLED

        return ListPickerState.ACTIVE

    def _handle_filter_input(self, key: str) -> ListPickerState:
        if len(key) == 1:
            # Handle simple keyboard presses first so they aren't interpreted as actions
            self._set_filter(self._filter + key)
            return ListPickerState.FILTERING

        match ACTION_BY_KEY.get(key, key):
            case (
                Action.UP
                | Action.DOWN
                | Action.PAGE_UP
                | Action.PAGE_DOWN
                | Action.TOP
                | Action.BOTTOM
                | Action.TOGGLE
                | Action.TOGGLE_ALL
            ):
                self._handle_main_input(key)
                return ListPickerState.ACTIVE
            case Action.HELP:
                return ListPickerState.HELP
            case Action.ERASE:
                self._set_filter(self._filter[: len(self._filter) - 1])
            case Action.ERASE_LINE:
                self._set_filter("")
            case Action.ACCEPT | Action.SUBMIT:
                return ListPickerState.ACTIVE
            case Action.CANCEL:
                self._set_filter("")
                return ListPickerState.ACTIVE
            case _:
                self._set_filter(self._filter + key)

        return ListPickerState.FILTERING

    def _handle_confirmation_input(self, key: str) -> ListPickerState:
        match ACTION_BY_KEY.get(key, key):
            case Action.HELP:
                return ListPickerState.HELP
            case "y" | "Y" | Action.ACCEPT | Action.SUBMIT:
                return ListPickerState.INACTIVE
            case _:
                return ListPickerState.ACTIVE

    def _handle_input(self, key: str) -> None:
        match self._state:
            case ListPickerState.ACTIVE:
                self._state = self._handle_main_input(key)
            case ListPickerState.FILTERING:
                self._state = self._handle_filter_input(key)
            case ListPickerState.HELP | ListPickerState.INFO:
                self._state = ListPickerState.ACTIVE  # All keypresses dismiss the panel and return to active state
            case ListPickerState.CONFIRMATION:
                self._state = self._handle_confirmation_input(key)
            case _:
                raise RuntimeError("impossible value for _state: %r" % self._state)

    def _run(self) -> None:
        self._selected_options.clear()
        self._selected_options.update(o for o in self._all_options if o.value in self._preselected_options)
        self._set_filter("")
        self._columns, self._lines = os.get_terminal_size(self._outfile.fileno())

        try:
            self._write_screen("\r\n" + CSI_CURSOR_HIDE)
            original_sigwinch_handler = signal.getsignal(signal.SIGWINCH)
            signal.signal(signal.SIGWINCH, self._sigwinch_handler)
            self._state = ListPickerState.ACTIVE

            while self._state.value >= ListPickerState.ACTIVE.value:
                try:
                    self._draw()
                    key = keyboard.getkey(self._infile)

                    if key is not None:
                        self._handle_input(key)

                except KeyboardInterrupt:  # try/except in a loop body has zero overhead in Python 3.11+ # noqa: PERF203
                    # Catch SIGINT here instead of using an asynchronous signal handler
                    # that will be hard to coordinate with this main thread
                    self._handle_input("Ctrl-C")

            match self._state:
                case ListPickerState.CANCELLED:
                    self._write_screen("\r\n")  # Leave list contents visible
                case ListPickerState.INACTIVE:
                    self._write_screen(self._clear_buffer_commands())

        finally:
            signal.signal(signal.SIGWINCH, original_sigwinch_handler)
            self._write_screen(CSI_CURSOR_SHOW)

    def pick(self) -> list[str]:
        self._run()
        return [o.value for o in self._all_options if o in self._selected_options]
