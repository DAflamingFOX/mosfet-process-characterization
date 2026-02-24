import os
import numpy as np
from matplotlib.ticker import EngFormatter

# Import our custom modules
from ltspice_parser import parse_ltspice_single, parse_ltspice_mirror
from characterization import extract_vth_and_kprime, extract_body_effect, extract_lambda
from plotting import plot_sqrt_id_vs_vgate, plot_lambda_fits


def process_device(
    device_type: str, single_file: str, mirror_file: str, L: float, W: float
):
    print(f"\n{'='*40}\nProcessing {device_type}\n{'='*40}")
    save_dir = "graphs/"
    os.makedirs(save_dir, exist_ok=True)

    single_sweeps = parse_ltspice_single(
        single_file, "V(vgs)" if device_type == "NMOS" else "V(vsg)", "Ibias"
    )
    vth_vals, k_prime, _, _ = extract_vth_and_kprime(single_sweeps, L, W)

    # NMOS V_T0 is positive. PMOS V_T0 is negative (but extracted from magnitude data)
    vt0 = vth_vals[0] if device_type == "NMOS" else -vth_vals[0]

    two_phi_f, gamma, _, _ = extract_body_effect(single_sweeps)

    lambda_sweeps = parse_ltspice_mirror(
        mirror_file,
        "V(vgs)" if device_type == "NMOS" else "V(vsg)",
        "Vdd",
        "I(Vsb)" if device_type == "NMOS" else "I(Vds)",
    )
    lambda_vals = extract_lambda(lambda_sweeps, vt0)

    # Generate plots
    slopes = [np.polyfit(np.sqrt(s.drain_current), s.gate_voltage, 1)[0] for s in single_sweeps]
    plot_sqrt_id_vs_vgate(single_sweeps, vth_vals, slopes, device_type, save_dir)
    plot_lambda_fits(lambda_sweeps, vt0, device_type, save_dir)

    # Print output
    fmt_k = EngFormatter(unit="A/V^2", places=3)
    fmt_v = EngFormatter(unit="V", places=3)
    fmt_g = EngFormatter(unit="V^1/2", places=3)
    fmt_l = EngFormatter(unit="V^-1", places=3)
    fmt_len = EngFormatter(unit="m", places=2)

    print(f"k'       = {fmt_k(k_prime)}")
    print(f"V_T0     = {fmt_v(vt0)}")
    print(f"2phi_F   = {fmt_v(two_phi_f)}")
    print(f"gamma    = {fmt_g(gamma)}")
    for i, lam in enumerate(lambda_vals):
        print(
            f"lambda_{i+1} = {fmt_l(lam)} (L = {fmt_len(lambda_sweeps[i].channel_length)})"
        )


if __name__ == "__main__":
    process_device(
        device_type="NMOS",
        single_file="ltspice/nmos_single_data.txt",
        mirror_file="ltspice/nmos_mirror_data.txt",
        L=2e-6,
        W=10e-6,
    )

    process_device(
        device_type="PMOS",
        single_file="ltspice/pmos_single_data.txt",
        mirror_file="ltspice/pmos_mirror_data.txt",
        L=2e-6,
        W=10e-6,
    )
