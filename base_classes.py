from dataclasses import dataclass
import numpy.typing as npt
import numpy as np


@dataclass
class ThermalLink:
    conductance: float

    def get_conductance(self, self_temp, other_temp):
        """
        Gets conductance as a result of self temperature and other temperature
        """
        return self.conductance


@dataclass
class ThermalSwitch(ThermalLink):
    cool_limit: float
    heat_limit: float
    attenuation_factor: float

    def get_conductance(self, self_temp, other_temp):
        """
        Gets conductance as a result of self temperature and other temperature

        Shuts off thermal link (decreasing its conductance) when it's either too
        hot or too cold
        """
        if other_temp > self_temp and self_temp > self.heat_limit:
            return self.conductance / self.attenuation_factor

        elif other_temp < self_temp and self_temp < self.cool_limit:
            return self.conductance / self.attenuation_factor

        else:
            return self.conductance


@dataclass
class HeatPump:
    """
    A heat pump is a device that moves heat from one place to another

    Generic base class, pumps zero heat
    """

    electrical_power: float  # W
    cop: float  # coefficient of performance
    set_temp: float  # K, heat pump turns off above this temperature

    def get_power(self, self_temp: float) -> float:
        return 0


@dataclass
class Refrigerator(HeatPump):
    """
    Subclass of heat pump that pumps heat from a cold place to a hot place
    """

    def get_power(self, self_temp: float) -> float:
        """
        Gets power as a result of self temperature and other temperature

        Continually pumps heat as long as it's not too cold
        """
        if self_temp > self.set_temp:
            # thermal power = electrical power * cop
            return self.electrical_power * self.cop
        else:
            return 0


@dataclass
class Heater:
    power: float  # W
    set_temp: float  # K, heater turns off above this temperature


@dataclass
class ThermalComponent:
    mass: float  # mass [kg]
    shc: float  # specific heat capacity [J/(kg*K)]
    rad_area: float  # radiative area [m^2]
    emissivity: float  # 0 to 1, emissivity

    temp: float  # temperature [K]
    illumination_factor: float  # 0 to 1; how much of the radiative area is lit by the Sun?
    innate_power: float  # intrinsic power generation factor, either from heaters or otherwise (W)

    heater: Heater  # electric heater used to keep the device warm

    @property
    def thermal_inertia(self) -> float:
        return self.mass * self.shc

    # power produced by electronics during operations
    def electronics_power(self, t: float) -> float:
        return 0


@dataclass
class ThermalArchitecture:
    components: list[ThermalComponent]
    conductivity_matrix: list[list[ThermalLink]]
    heat_pump_matrix: list[list[HeatPump]]

    def to_state(self) -> npt.NDArray[np.floating]:
        # Turns the spacecraft thermal architecture into a state form
        # (just the temperatures)
        return np.array([component.temp for component in self.components])

    def update_from_state(self, temps: npt.NDArray[np.floating]):
        # Update state to spacecraft properties
        for idx, component in enumerate(self.components):
            component.temp = temps[idx]

    @property
    def component_thermal_inertias(self) -> npt.NDArray[np.floating]:
        return np.array([component.thermal_inertia for component in self.components])


@dataclass
class EnvironmentalConditions:
    name: str
    sunlit_radiative_flux: float  # W/m^2
    background_temp: float  # K, usually the temperature of space, 2.7 K
    orbital_period: float
    sunlit_period: float

    def incident_radiative_flux(self, t: float):
        if t % self.orbital_period < self.sunlit_period:
            return self.sunlit_radiative_flux
        else:
            return 0
