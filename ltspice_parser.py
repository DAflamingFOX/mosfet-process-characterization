import numpy as np
from dataclasses import dataclass
from typing import List


@dataclass
class SweepData:
    """Holds data for a single step in a parametric sweep."""

    step_value: float
    x_data: np.ndarray
    y_data: np.ndarray


def parse_ltspice_value(val_str: str) -> float:
    """Converts LTSpice strings with unit suffixes (e.g., '300n', '50m') to floats."""
    val_str = val_str.lower().strip()
    units = {
        "f": 1e-15,
        "p": 1e-12,
        "n": 1e-9,
        "µ": 1e-6,
        "m": 1e-3,
        "k": 1e3,
        "meg": 1e6,
        "g": 1e9,
    }
    for unit, multiplier in units.items():
        if val_str.endswith(unit):
            return float(val_str[: -len(unit)]) * multiplier
    return float(val_str)


def parse_ltspice_txt(filename: str, x_col: int, y_col: int) -> List[SweepData]:
    """
    Parses exported LTSpice text data into a list of SweepData objects.
    Allows specifying which column represents the X (voltage) and Y (current) data.
    """
    sweeps = []
    current_x, current_y = [], []
    step_val = 0.0

    with open(filename, "r", encoding="latin-1") as f:
        lines = f.readlines()

    for line in lines[1:]:  # Skip the header
        line = line.strip()
        if not line:
            continue

        if line.startswith("Step Information:"):
            if current_x:
                sweeps.append(
                    SweepData(
                        step_value=step_val,
                        x_data=np.array(current_x, dtype=float),
                        y_data=np.array(current_y, dtype=float),
                    )
                )
                current_x, current_y = [], []

            # Extract just the unit value string (e.g., "500m")
            raw_val = line.split("=")[1].split(" ")[0]
            step_val = parse_ltspice_value(raw_val)
        else:
            parts = line.split()
            try:
                current_x.append(float(parts[x_col]))
                current_y.append(float(parts[y_col]))
            except (ValueError, IndexError):
                continue

    # Append the final block of data
    if current_x:
        sweeps.append(
            SweepData(
                step_value=step_val,
                x_data=np.array(current_x, dtype=float),
                y_data=np.array(current_y, dtype=float),
            )
        )

    return sweeps
