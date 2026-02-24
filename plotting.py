import matplotlib.pyplot as plt
import numpy as np
from typing import List
from ltspice_parser import SingleSweepData, MirrorSweepData


def plot_sqrt_id_vs_vgate(
    sweeps: List[SingleSweepData],
    vth_vals: np.ndarray,
    slopes: List[float],
    device_type: str,
    save_dir: str,
):
    """Plots the square root of drain current vs gate voltage to visualize threshold voltages."""
    plt.figure(figsize=(10, 7))
    # colors = ["b", "g", "r", "c"]

    vg_label = r"$V_{gs}$" if device_type == "NMOS" else r"$V_{sg}$"
    vb_label = r"$V_{sb}$" if device_type == "NMOS" else r"$V_{bs}$"
    vt_label = r"$V_{T}$" if device_type == "NMOS" else r"$\|V_{T}\|$"

    for i, sweep in enumerate(sweeps):
        sqrt_id = np.sqrt(sweep.drain_current)
        v_gate = sweep.gate_voltage

        b, m = vth_vals[i], slopes[i]
        x_fit = np.linspace(b - 0.01, v_gate[-1], 100)

        plt.plot(x_fit, (x_fit - b) / m)
        plt.plot(
            v_gate,
            sqrt_id,
            "s",
            markersize=3,
            label=f"{vb_label}={sweep.body_voltage}V",
        )

    # Plot baseline and Vth markers
    plt.plot(
        np.linspace(min(vth_vals) - 0.1, max(sweep.gate_voltage), 100),
        np.zeros(100),
        "m--",
    )
    plt.plot(vth_vals, np.zeros(len(vth_vals)), "k*", label=vt_label)

    plt.grid(True, alpha=0.5)
    plt.xlabel(f"{vg_label} (V)")
    plt.ylabel(r"$\sqrt{I_{d}}$ $(A^{1/2})$")
    plt.title(rf"$\sqrt{{I_{{d}}}}$ vs {vg_label}")
    plt.legend(loc="upper left")
    plt.savefig(f"{save_dir}{device_type.lower()}_sqrt_id_vs_vgate.png", dpi=300)
    plt.close()


def plot_lambda_fits(
    sweeps: List[MirrorSweepData],
    vt0: float,
    device_type: str,
    save_dir: str,
    v_range: float = 0.2,
    margin: float = 0.05,
):
    """Plots drain current vs drain voltage and highlights the linear fit window used for lambda."""
    plt.figure(figsize=(10, 7))
    # colors = ["b", "g", "r", "c", "m"]

    vd_label = r"$V_{ds}$" if device_type == "NMOS" else r"$V_{sd}$"
    L_label = r"$L_{n}$" if device_type == "NMOS" else r"$L_{p}$"

    for i, sweep in enumerate(sweeps):
        plt.plot(
            sweep.supply_voltage,
            sweep.drain_current,
            ".",
            markersize=2,
            # color=colors[i],
            label=f"{L_label}={sweep.channel_length:.2e}m",
        )

        v_ds_sat = sweep.gate_voltage - np.abs(vt0)

        v_start = v_ds_sat + margin
        v_end = v_start + v_range

        mask = (sweep.supply_voltage >= v_start) & (sweep.supply_voltage <= v_end)
        p = np.polyfit(sweep.supply_voltage[mask], sweep.drain_current[mask], deg=1)
        x_fit = np.linspace(v_start, v_end, 100)
        plt.plot(x_fit, p[0] * x_fit + p[1], "y", linewidth=3)

    plt.grid(True, alpha=0.5)
    plt.xlabel(f"{vd_label} (V)")
    plt.ylabel(r"$I_{d}$ (A)")
    plt.title(f"$I_{{d}}$ vs {vd_label} with Estimation Windows")
    plt.legend(loc="upper left")
    plt.savefig(f"{save_dir}{device_type.lower()}_id_vs_vds.png", dpi=300)
    plt.close()
