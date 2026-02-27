import numpy as np
from typing import Tuple, List
from ltspice_parser import SingleSweepData, MirrorSweepData


def extract_vth_and_kprime(
    sweeps: List[SingleSweepData], L: float, W: float
) -> Tuple[np.ndarray, float, np.ndarray, float]:
    """
    Extracts Threshold Voltages, K-prime, and error norms.
    V_gs = m * sqrt(I_d) + V_T  --> m = sqrt(2L / (k'W))
    """
    vth_list, slopes, errors = [], [], []

    for sweep in sweeps:
        p, residuals, _, _, _ = np.polyfit(
            np.sqrt(sweep.drain_current), sweep.gate_voltage, deg=1, full=True
        )
        slopes.append(p[0])
        vth_list.append(p[1])  # Intercept is V_T
        errors.append(np.sqrt(residuals[0]) if residuals.size > 0 else 0)

    m_0 = slopes[0]
    k_prime = (2 * L) / (W * (m_0**2))

    return np.array(vth_list), k_prime, np.array(errors), slopes[0]


def extract_body_effect(
    sweeps: List[SingleSweepData],
) -> Tuple[float, float, float, int]:
    """
    Solves for 2*Phi_f and Gamma.
    V_T = V_T0 + gamma * (sqrt(2phi_f + V_sb) - sqrt(2phi_f))
    """
    num_sweeps = len(sweeps)

    # We need 1 reference sweep + at least 3 biased sweeps to get 2 sequential error terms
    if num_sweeps < 4:
        raise ValueError(
            f"At least 4 sweeps are required to generate a minimum of 2 error terms."
            f"Received {num_sweeps} sweep(s)."
        )

    # Extract Vth and V_body for all sweeps
    v_body_vals = np.array([s.body_voltage for s in sweeps])
    vth_vals = np.array(
        [np.polyfit(np.sqrt(s.drain_current), s.gate_voltage, deg=1)[1] for s in sweeps]
    )

    # a_vals represent delta V_T for the biased sweeps
    a_vals = vth_vals[1:] - vth_vals[0]

    # Calculate measured ratios: a_{i+1} / a_{i}
    measured_ratios = a_vals[1:] / a_vals[:-1]

    # Generate tpf values
    tpf_vals = np.linspace(0, 2, 10_000)

    # Reshape tpf_vals to a column vector for broadcasting against body voltages
    tpf_grid = tpf_vals[:, np.newaxis]
    vb_grid = v_body_vals[1:]

    # Calculate gamma_terms for all tpf values and all biased sweeps simultaneously
    gamma_terms = np.sqrt(tpf_grid + vb_grid) - np.sqrt(tpf_grid)

    # Calculate theoretical ratios: gamma_term_{i+1} / gamma_term_{i}
    theoretical_ratios = gamma_terms[:, 1:] / gamma_terms[:, :-1]

    # Calculate residuals (L2 norm / 2-norm across all error terms for a given tpf)
    errors = theoretical_ratios - measured_ratios
    residuals = np.sqrt(np.sum(errors**2, axis=1))

    # Extract the best fit parameters
    best_idx = np.argmin(residuals)
    two_phi_f = tpf_vals[best_idx]
    best_error = residuals[best_idx]

    # Linear fit for Gamma using all sweeps
    x_vals = np.sqrt(two_phi_f + v_body_vals) - np.sqrt(two_phi_f)
    y_vals = vth_vals - vth_vals[0]

    p = np.polyfit(x_vals, y_vals, deg=1)
    gamma = p[0]

    return two_phi_f, gamma, tpf_vals, residuals, best_idx


def extract_lambda(
    sweeps: List[MirrorSweepData],
    vt0: float,
    v_range: float = 0.2,
    margin: float = 0.05,
) -> List[float]:
    """
    Extracts channel length modulation parameter (lambda) over various lengths.
    Uses a defined linear region (v_start to v_start + v_range) for extraction.
    """
    lambda_vals = []

    for sweep in sweeps:
        # Calculate the saturation boundary
        v_ds_sat = sweep.gate_voltage - np.abs(vt0)

        # Define window for linear fit
        v_start = v_ds_sat + margin
        v_end = v_start + v_range

        mask = (sweep.supply_voltage >= v_start) & (sweep.supply_voltage <= v_end)

        p = np.polyfit(sweep.supply_voltage[mask], sweep.drain_current[mask], deg=1)

        m, b = p[0], p[1]

        lambda_vals.append(m / b)

    return lambda_vals
