from base_classes import ThermalComponent, Heater
from environmental_prefabs import (
    ORBITAL_PERIOD,
    END_OF_PRE_COLLECT,
    END_OF_EARTH_COMMS,
    END_OF_COLLECT,
    END_OF_ORBIT_ADJUSTMENT,
    END_OF_SUNLIT_PERIOD,
)

# Initial temperature does not matter for these
# Illumination factor also does not matter so much


def get_components() -> list[ThermalComponent]:
    """
    Returns spacecraft components based on case flags

    Parameters
    ----------
    case_flags: dict
        dictionary of case flags


    Returns
    -------
    list[ThermalComponent]
        list of spacecraft components
    """

    """
    Main Body
    Mass: 7500 kg
    Heat Capacity: 890 J/kg/K
    Radiative Area: 230 m^2 (mainly the solar arrays)
    Emisivity: 0.95, divided by 40 for MLI
    Temperature: 293 K
    Illumination Factor: 0.33 - 33% sunlit, 67% dark/radiating
    Heating power: 900 W, set to 220 K setpoint
    RHU power: 100 W
    """

    MAIN_BODY = ThermalComponent(
        mass=7500,
        shc=890,
        rad_area=40,
        emissivity=0.95 / 40,
        temp=300,
        illumination_factor=0.33,
        innate_power=120,  # RHUs
        heater=Heater(power=400, set_temp=300),
    )

    def spacecraft_power(t: float) -> float:
        """
        Returns computer power in W.

        Convention: postive number = power in

        Parameters
        ----------
        t: float
            time (s)

        Returns
        -------
        float
            power in (W)
        """
        if t % ORBITAL_PERIOD < END_OF_SUNLIT_PERIOD:
            return 590
        elif t % ORBITAL_PERIOD < END_OF_EARTH_COMMS:
            return 805
        elif t % ORBITAL_PERIOD < END_OF_ORBIT_ADJUSTMENT:
            return 754
        elif t % ORBITAL_PERIOD < END_OF_PRE_COLLECT:
            return 742
        elif t % ORBITAL_PERIOD < END_OF_COLLECT:
            return 808
        else:
            raise ValueError("something is wrong!")

    MAIN_BODY.electronics_power = spacecraft_power

    """
    COLLECTOR SHELL
    more poorly insulated, but smaller area
    no built in heaters
    10 W of waste heat
    """
    SAMPLE_SHELL = ThermalComponent(
        mass=150,
        shc=890,
        rad_area=10,
        emissivity=0.95 / 5,
        temp=165,
        illumination_factor=0.7,
        innate_power=10,
        heater=Heater(power=0, set_temp=0),
    )

    """
    SAMPLES IN AEROGEL ARRAY
    """
    SAMPLES = ThermalComponent(
        mass=0.1,
        shc=4186,
        rad_area=0,
        emissivity=0,
        temp=165,
        illumination_factor=0,
        innate_power=0,
        heater=Heater(power=0, set_temp=0),
    )

    """
    SOLAR ARRAYS
    Insulated similarly to the main body
    """
    SOLAR_ARRAYS = ThermalComponent(
        mass=700,
        shc=890,
        rad_area=230,
        emissivity=0.95 / 40,
        temp=265,
        illumination_factor=0.5,
        innate_power=0,
        heater=Heater(power=0, set_temp=0),
    )

    return [MAIN_BODY, SAMPLE_SHELL, SAMPLES, SOLAR_ARRAYS]
