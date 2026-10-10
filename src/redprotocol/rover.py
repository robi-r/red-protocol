"""Rover hardware parameters and the student-facing action vocabulary."""
from dataclasses import dataclass

MODES = {"sleep": 5.0, "science": 40.0, "drive": 120.0}  # electrical draw in watts


@dataclass
class RoverSpec:
    battery_capacity_wh: float = 1200.0
    panel_area_m2: float = 3.0
    panel_efficiency: float = 0.25
    heater_power_w: float = 60.0
    thermal_mass_j_per_k: float = 50_000.0
    insulation_w_per_k: float = 1.0
    min_survival_temp_k: float = 233.0   # -40 C: electronics fail below this
    start_battery_frac: float = 1.0
    start_internal_temp_k: float = 260.0
