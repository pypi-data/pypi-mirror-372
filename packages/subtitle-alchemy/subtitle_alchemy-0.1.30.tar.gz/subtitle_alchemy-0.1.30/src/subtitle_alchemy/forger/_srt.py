"""Timeline utility functions."""

from pathlib import Path

import numpy as np

from subtitle_alchemy.utils import timeline


def _hmss2srttl(tl: np.ndarray) -> np.ndarray:
    """Format the HH:MM:SS.mmm array to SRT timeline string.

    Args:
        tl (np.ndarray): 2D array (N, 8) of hours, minutes, seconds, and ms

    Returns:
        np.ndarray: 1D array (N,) of SRT timeline strings
        - 00:00:07,000 --> 00:00:10,500
    """
    return np.array(
        [
            f"{hmss[0]:02d}:{hmss[2]:02d}:{hmss[4]:02d},{hmss[6]:03d} --> "
            f"{hmss[1]:02d}:{hmss[3]:02d}:{hmss[5]:02d},{hmss[7]:03d}"
            for hmss in tl
        ],
        dtype="U29",
    )


def gen_srt(ms: np.ndarray, text: np.ndarray, path: Path) -> None:
    """Generate an SRT file from the timeline and text arrays.

    Args:
        ms (np.ndarray): 2D array (N, 2) of milliseconds
        text (np.ndarray): 1D array (N,) of text
        path (Path): Path to save the SRT file
    """
    hmss = timeline.ms2hmss(ms)
    tl_str = _hmss2srttl(hmss)

    with open(path, "w") as f:
        for i, (hmss, txt) in enumerate(zip(tl_str, text, strict=True)):
            f.write(f"{i+1}\n")
            f.write(f"{hmss}\n")
            f.write(f"{txt}\n")
            f.write("\n")
