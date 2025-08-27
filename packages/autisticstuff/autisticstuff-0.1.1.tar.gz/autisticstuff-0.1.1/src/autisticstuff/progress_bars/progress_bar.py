"""Module with basic progress bar"""

import time
from collections.abc import Iterable
from typing import Any
from sys import stdout
from autisticstuff.progress_bars.utils import draw_circle, draw_fluid

from autisticstuff.progress_bars.enums import Styles
import re


def progress_bar(
        iterable: int | Iterable[Any],
        max_length: int = None,
        title: str = "",
        main_char: str = "█",
        space_char: str = "░",
        size: int = 50,
        show_percentage: bool = True,
        show_count: bool = True,
        style: Styles = Styles.CIRCLE,
):
    if max_length is None:
        try:
            max_length = len(iterable)
        except TypeError as exc:
            raise ValueError(
                "Если передан итерируемый объект без длины, нужно явно указать max_length"
            ) from exc
    for idx, _ in enumerate(iterable, 1):
        perc_complete = int(idx * 100 / max_length)
        percent_str = f" ({perc_complete}%)"
        num_bars = int(perc_complete * size / 100)
        _progress_bar = "[" + main_char * num_bars + space_char * (size - num_bars) + "]"
        count_str = f" {idx}/{max_length}"
        custom_title = "Do something..."
        match style:
            case Styles.CLASSIC:
                text = f"\r{title if title else custom_title} - {_progress_bar}{count_str if show_count else ''}"
            case Styles.CIRCLE:
                cir = draw_circle(size, perc_complete, main_char, space_char,
                                  title=f"{percent_str if show_percentage else title}")
                text = f"\r{cir}\n\n\r{title if show_percentage else ""}"
            case Styles.FLUID:
                cir = draw_fluid(size, perc_complete, main_char, space_char,
                                 title=f"{percent_str if show_percentage else title}")
                text = f"\r{cir}\n\n\r{title if show_percentage else ""}"

        yield text
    return None


if __name__ == "__main__":
    # Example
    for text in progress_bar(range(100), title="Do something...", show_percentage=True, size=15, style=Styles.FLUID):
        stdout.write("\r" + text)
        stdout.flush()
        time.sleep(0.01)
    stdout.write("\n")
