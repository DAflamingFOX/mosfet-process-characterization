import numpy as np
from dataclasses import dataclass
from typing import List


@dataclass
class SingleSweepData:
    """Holds data for a single step in a parametric sweep for the single MOSFET schematic."""

    body_voltage: float
    gate_voltage: np.ndarray
    drain_current: np.ndarray


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


def parse_ltspice_single(
    filename: str, gate_voltage_name: str, drain_current_name: str
) -> List[SingleSweepData]:
    """
    Parses exported LTSpice text data into a list of SingleSweepData objects.
    """

    sweeps = []
    current_gate_voltage, current_drain_current = [], []
    step_val = 0.0

    with open(filename, "r", encoding="latin-1") as f:
        lines = f.readlines()

    if not lines:
        return []

    # Parse header line
    headers = lines[0].strip().split()
    column_indicies = {name: index for index, name in enumerate(headers)}

    # Verify the columns we expect are present.
    if drain_current_name not in column_indicies:
        raise ValueError(
            f"Column {drain_current_name} not found. Available columns: {headers}"
        )
    if gate_voltage_name not in column_indicies:
        raise ValueError(
            f"Column {gate_voltage_name} not found. Available columns: {headers}"
        )

    # Assign the correct indicies dynamically
    gate_voltage_col = column_indicies[gate_voltage_name]
    drain_current_col = column_indicies[drain_current_name]

    # Iterate through the rest of the data.
    for line in lines[1:]:  # Skip the header
        line = line.strip()
        if not line:
            continue

        if line.startswith("Step Information:"):
            # If we have collected data, save it as a complete sweep before starting the next.
            if current_drain_current:
                sweeps.append(
                    SingleSweepData(
                        body_voltage=step_val,
                        drain_current=np.array(current_drain_current, dtype=float),
                        gate_voltage=np.array(current_gate_voltage, dtype=float),
                    )
                )
                current_gate_voltage, current_drain_current = [], []

            # Extract just the unit value string (e.g., "500m")
            raw_val = line.split("=")[1].split(" ")[0]
            step_val = parse_ltspice_value(raw_val)
        else:
            parts = line.split()
            try:
                current_drain_current.append(float(parts[drain_current_col]))
                current_gate_voltage.append(float(parts[gate_voltage_col]))
            except (ValueError, IndexError):
                continue

    # Append the final block of data
    if current_drain_current:
        sweeps.append(
            SingleSweepData(
                body_voltage=step_val,
                drain_current=np.array(current_drain_current, dtype=float),
                gate_voltage=np.array(current_gate_voltage, dtype=float),
            )
        )

    return sweeps


@dataclass
class MirrorSweepData:
    """Holds data for a single step in a parametric sweep for the simple current mirror MOSFET schematic."""

    channel_length: float
    gate_voltage: np.ndarray
    supply_voltage: np.ndarray
    drain_current: np.ndarray


def parse_ltspice_mirror(
    filename: str,
    gate_voltage_name: str,
    supply_voltage_name: str,
    drain_current_name: str,
) -> List[MirrorSweepData]:
    """
    Parses exported LTSpice text data into a list of SingleSweepData objects.
    """

    sweeps = []
    current_gate_voltage, current_drain_current, current_supply_voltage = [], [], []
    step_val = 0.0

    with open(filename, "r", encoding="latin-1") as f:
        lines = f.readlines()

    if not lines:
        return []

    # Parse header line
    headers = lines[0].strip().split()
    column_indicies = {name: index for index, name in enumerate(headers)}

    # Verify the columns we expect are present.
    if drain_current_name not in column_indicies:
        raise ValueError(
            f"Column {drain_current_name} not found. Available columns: {headers}"
        )
    if gate_voltage_name not in column_indicies:
        raise ValueError(
            f"Column {gate_voltage_name} not found. Available columns: {headers}"
        )
    if supply_voltage_name not in column_indicies:
        raise ValueError(
            f"Column {supply_voltage_name} not found. Available columns: {headers}"
        )

    # Assign the correct indicies dynamically
    gate_voltage_col = column_indicies[gate_voltage_name]
    drain_current_col = column_indicies[drain_current_name]
    supply_voltage_col = column_indicies[supply_voltage_name]

    # Iterate through the rest of the data.
    for line in lines[1:]:  # Skip the header
        line = line.strip()
        if not line:
            continue

        if line.startswith("Step Information:"):
            # If we have collected data, save it as a complete sweep before starting the next.
            if current_drain_current:
                sweeps.append(
                    MirrorSweepData(
                        channel_length=step_val,
                        drain_current=np.array(current_drain_current, dtype=float),
                        gate_voltage=np.array(current_gate_voltage, dtype=float),
                        supply_voltage=np.array(current_supply_voltage, dtype=float),
                    )
                )
                current_gate_voltage = []
                current_drain_current = []
                current_supply_voltage = []

            # Extract just the unit value string (e.g., "500m")
            raw_val = line.split("=")[1].split(" ")[0]
            step_val = parse_ltspice_value(raw_val)
        else:
            parts = line.split()
            try:
                current_drain_current.append(float(parts[drain_current_col]))
                current_gate_voltage.append(float(parts[gate_voltage_col]))
                current_supply_voltage.append(float(parts[supply_voltage_col]))
            except (ValueError, IndexError):
                continue

    # Append the final block of data
    if current_drain_current:
        sweeps.append(
            MirrorSweepData(
                channel_length=step_val,
                drain_current=np.array(current_drain_current, dtype=float),
                gate_voltage=np.array(current_gate_voltage, dtype=float),
                supply_voltage=np.array(current_supply_voltage, dtype=float),
            )
        )

    return sweeps
