from base_classes import (
    ThermalArchitecture,
    ThermalLink,
    HeatPump,
    Refrigerator,
)
from component_prefabs import get_components

conductivity_matrix = [[ThermalLink(conductance=0) for _ in range(4)] for _ in range(4)]

al_thermal_conductivity = 237  # W/mK
face_cross_sectional_area = 1  # m^2; sum of support structures
isolation_length = 2  # m
insulation_factor = 400
body_to_shell_conductance = (
    al_thermal_conductivity
    * face_cross_sectional_area
    / isolation_length
    / insulation_factor
)

# Main Body <-> Shell
conductivity_matrix[0][1] = ThermalLink(conductance=body_to_shell_conductance)

aerogel_thermal_conductivity = 0.02  # W/mK
aerogel_length = 0.1  # m
aerogel_area = 7.065  # m^2
sample_to_shell_conductance = (
    aerogel_thermal_conductivity * aerogel_area / aerogel_length
)
# Shell <-> Samples
conductivity_matrix[1][2] = ThermalLink(conductance=sample_to_shell_conductance)

solar_array_joint_area = 0.1  # m^2
solar_array_joint_length = 0.1  # m
solar_array_joint_conductance = (
    al_thermal_conductivity * solar_array_joint_area / solar_array_joint_length
)

# Body <-> Solar Arrays
conductivity_matrix[0][3] = ThermalLink(conductance=solar_array_joint_conductance / 10)

# Symmetrize Matrix
for i in range(int(len(conductivity_matrix) / 2)):
    for j in range(len(conductivity_matrix)):
        conductivity_matrix[j][i] = conductivity_matrix[i][j]


# Set up heat pumps
heat_pump_matrix = [
    [HeatPump(electrical_power=0, cop=0, set_temp=0) for _ in range(4)]
    for _ in range(4)
]

# Shell -> Body
heat_pump_matrix[1][0] = Refrigerator(electrical_power=50, cop=1, set_temp=160)


def get_srs(heat_pump: bool = False) -> ThermalArchitecture:
    """
    Returns the sample return spacecraft thermal architecture

    Returns
    -------
    ThermalArchitecture
        the spacecraft thermal architecture
    """
    if not heat_pump:
        heat_pump_matrix[1][0] = HeatPump(electrical_power=0, cop=0, set_temp=0)

    return ThermalArchitecture(
        get_components(),
        # Symmetric matrix
        conductivity_matrix=conductivity_matrix,
        heat_pump_matrix=heat_pump_matrix,
    )
