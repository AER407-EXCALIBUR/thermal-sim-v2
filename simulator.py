from matplotlib import pyplot as plt
from scipy.integrate import solve_ivp

from base_classes import EnvironmentalConditions, ThermalArchitecture
from environmental_prefabs import ENCELADUS, ORBITAL_PERIOD
from odes import thermal_ode
from spacecraft_prefabs import get_srs
import numpy as np


def run_sim(
    spacecraft: ThermalArchitecture,
    case_name: str,
    environment: EnvironmentalConditions,
    show: bool = False,
):
    """
    Runs a simulation of the thermal architecture
    """
    sol = solve_ivp(
        thermal_ode,
        (0, 10 * ORBITAL_PERIOD),
        list(spacecraft.to_state()) + [0, 0, 0, 0],
        args=(spacecraft, environment),
        method="RK23",
        atol=1e-6,
    )

    # Plot
    fig, ax = plt.subplots(figsize=(10, 7))

    ax.plot(sol.t, sol.y[0, :], label="Main Body", color="red")
    ax.plot(sol.t, sol.y[3, :], label="Solar Arrays", color="blue")
    ax.plot(sol.t, sol.y[1, :], label="SCM Shell", color="green")
    ax.plot(sol.t, sol.y[2, :], label="Samples", color="cyan", linestyle="--")
    ax.set_ylabel("Component Temperature (K)")
    ax.set_xlabel("Time (s)")
    ax.grid()
    ax.set_title(f"Thermal Sim - {environment.name}\n" + case_name)

    # Plot heating load
    solar_flux = np.zeros_like(sol.t)

    for i, time in enumerate(sol.t):
        solar_flux[i] = environment.incident_radiative_flux(time)

    ax.fill_between(
        sol.t,
        np.min(sol.y[:4, :]),
        np.max(sol.y[:4, :]),
        solar_flux > 0,
        alpha=0.2,
        color="yellow",
    )
    ax.fill_between(
        sol.t,
        np.min(sol.y[:4, :]),
        np.max(sol.y[:4, :]),
        solar_flux < 1,
        alpha=0.2,
        color="black",
    )

    ax.legend()

    fig.savefig(f"outputs/{environment.name}_case_{case_name}.png", dpi=300)
    with open(f"outputs/{environment.name}_case_{case_name}.txt", "w") as f:
        labels = [
            "Avg RHU + Electronics Heating Power",
            "Avg Heater and Pump Power",
            "Avg Incoming Radiative Power",
            "Avg Rejected Radiative Power",
        ]

        for idx, label in enumerate(labels):
            num_components = len(spacecraft.components)

            power_value = (
                sol.y[num_components + idx, -1] - sol.y[num_components + idx, 0]
            ) / (sol.t[-1] - sol.t[0])
            f.write(f"{label}: {power_value:.2f} W\n")

    if show:
        plt.show()


if __name__ == "__main__":
    run_sim(
        get_srs(heat_pump=True),
        "With Heat Pump",
        ENCELADUS,
        show=False,
    )

    run_sim(
        get_srs(heat_pump=False),
        "Without Heat Pump",
        ENCELADUS,
        show=False,
    )
