from base_classes import ThermalComponent, EnvironmentalConditions, ThermalLink
from scipy.constants import Stefan_Boltzmann


def incident_radiation_flux(
    t: float,
    component: ThermalComponent,
    environment: EnvironmentalConditions,
) -> float:
    """
    Returns incident radiation power in W.

    Convention: postive number = flux in

    Sunlit during t = 0 to 34853

    Parameters
    ----------
    t: float
        time (s)
    component: ThermalComponent
        component which we are transferring heat to
    environment: EnvironmentalConditions
        environmental conditions surrounding the spacecraft

    Math
    ----
    * Assume the radiative flux source produces x W/m^2 of radiation at some point
    * We therefore absorb x * (total radiative surface area) * (proportion of surface area which is illuminated) * emissivity
    """

    return (
        environment.incident_radiative_flux(t)
        * component.rad_area
        * component.illumination_factor
        * component.emissivity
    )


def background_radiation_flux(
    component: ThermalComponent, environment: EnvironmentalConditions
) -> float:
    """
    Returns radiation power from interactions with the background of space, in W.

    Convention: postive number = flux in

    Parameters
    ----------
    component: ThermalComponent
        component which we are transferring heat to
    environment: EnvironmentalConditions
        environmental conditions surrounding the spacecraft

    Math
    ----
    Q = (Stefan Boltzmann CNST) * emissivity * A * (T1**4 - T2**4) = Heat going from 1 -> 2
    """

    background_radiating_area = component.rad_area * (1 - component.illumination_factor)

    return (
        Stefan_Boltzmann
        * (environment.background_temp**4 - component.temp**4)
        * background_radiating_area
        * component.emissivity
    )


def conduction_flux(
    component_1: ThermalComponent,
    component_2: ThermalComponent,
    thermal_link: ThermalLink,
) -> float:
    """
    Calculates conduction flux from component 1 to component 2

    https://www.nasa.gov/smallsat-institute/sst-soa/thermal-control/
    section 7.2.4

    Parameters
    ----------
    component_1: ThermalComponent
        source component
    component_2: ThermalComponent
        sink component
    k: float
        thermal conductance (W/K)
    """

    return thermal_link.get_conductance(component_2.temp, component_1.temp) * (
        component_1.temp - component_2.temp
    )
