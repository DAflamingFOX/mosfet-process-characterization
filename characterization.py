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

    vth_vals = []
    v_body_vals = np.array([sweep.body_voltage for sweep in sweeps])

    for sweep in sweeps:
        _, b = np.polyfit(np.sqrt(sweep.drain_current), sweep.gate_voltage, deg=1)
        vth_vals.append(b)

    a1 = vth_vals[1] - vth_vals[0]
    a2 = vth_vals[2] - vth_vals[0]
    a3 = vth_vals[3] - vth_vals[0]

    gamma_term = lambda tpf, vb: np.sqrt(tpf + vb) - np.sqrt(tpf)

    e1 = lambda tpf: (
        gamma_term(tpf, v_body_vals[2]) / gamma_term(tpf, v_body_vals[1])
    ) - (a2 / a1)
    e2 = lambda tpf: (
        gamma_term(tpf, v_body_vals[3]) / gamma_term(tpf, v_body_vals[2])
    ) - (a3 / a2)
    twonorm = lambda e1, e2: np.sqrt(e1**2 + e2**2)

    tpf_vals = np.linspace(0.3, 1.3, 10_000)
    residuals = np.array([twonorm(e1(tpf), e2(tpf)) for tpf in tpf_vals])

    best_idx = np.argmin(residuals)
    two_phi_f = tpf_vals[best_idx]
    best_error = residuals[best_idx]

    # Linear fit for Gamma
    x_vals = np.array([gamma_term(two_phi_f, vb) for vb in v_body_vals])
    y_vals = vth_vals - vth_vals[0]

    p, _, _, _, _ = np.polyfit(x_vals, y_vals, deg=1, full=True)
    gamma = p[0]

    return two_phi_f, gamma, best_error, best_idx


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

        lambda_vals.append(m/b)

    return lambda_vals
