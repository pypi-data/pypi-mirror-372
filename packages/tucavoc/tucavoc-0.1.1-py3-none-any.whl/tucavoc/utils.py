from datetime import timedelta
from pathlib import Path
import pandas as pd
import numpy as np


def guess_calib_substances(
    calib_values: list[float],
    blank_values: list[float],
    std_threshold: float = 3.0,
) -> bool:
    """Geuss if the substance is present in the calibration or not."""
    blank_mean = np.mean(blank_values)
    calib_mean = np.mean(calib_values)

    return bool(calib_mean > (blank_mean * std_threshold))
