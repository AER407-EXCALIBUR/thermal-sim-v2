import numpy as np
from base_classes import ThermalArchitecture, EnvironmentalConditions

from heat_transfer import (
    incident_radiation_flux,
    background_radiation_flux,
    conduction_flux,
)


def thermal_ode(
    t: float,
    y: np.ndarray,
    spacecraft: ThermalArchitecture,
    environment: EnvironmentalConditions,
) -> np.ndarray:
    """
    Computes heat transfer between components of the spacecraft and the environment

    Parameters
    ----------
    t: float
        time (s)
    y: np.ndarray
        state vector, temperatures of the components in K
    spacecraft: ThermalArchitecture
        spacecraft thermal architecture
    environment: EnvironmentalConditions
        environmental conditions surrounding the spacecraft

    Returns
    -------
    np.ndarray
        derivative of the state vector, temperatures of the components in K/s

    Math
    ----
    dT/dt = (Q_in - Q_out) / (thermal inertia)
    """
    num_components = len(spacecraft.components)

    # Update temperatures
    spacecraft.update_from_state(y[0:num_components])

    # Get temperatures from spacecraft
    temps = spacecraft.to_state()
    assert np.allclose(temps, y[0:num_components])

    fluxes = np.zeros_like(temps)
    yp = np.zeros_like(y)

    for i, component in enumerate(spacecraft.components):
        # 1A. Innate power
        fluxes[i] += component.innate_power
        yp[num_components] += component.innate_power  # recording

        # 1B. Heaters
        if component.temp < component.heater.set_temp:
            fluxes[i] += component.heater.power
            yp[num_components + 1] += component.heater.power  # recording

        # 1C. Electronics
        fluxes[i] += component.electronics_power(t)
        yp[num_components] += component.electronics_power(t)  # recording

        # 2A. Radiation flux
        incident_flux = incident_radiation_flux(t, component, environment)
        background_flux = background_radiation_flux(component, environment)

        yp[num_components + 2] += incident_flux  # recording
        yp[num_components + 3] += background_flux  # recording
        fluxes[i] += incident_flux + background_flux

        # 3. Conduction flux & pump flux
        for j, other_component in enumerate(spacecraft.components):
            fluxes[i] += conduction_flux(
                other_component, component, spacecraft.conductivity_matrix[i][j]
            )

            # if component i has a heat pump to component j, we need to add the heat pump power
            # to j, and subtract it from i
            pump_flux = spacecraft.heat_pump_matrix[i][j].get_power(temps[i])
            fluxes[i] -= pump_flux
            fluxes[j] += pump_flux
            yp[num_components + 1] += pump_flux  # recording

    # Divide fluxes by component inertia
    yp[0:num_components] = fluxes / spacecraft.component_thermal_inertias

    # power draw included in yp
    return yp
