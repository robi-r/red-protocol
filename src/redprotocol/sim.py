"""Simulation engine. No UI code here, so it runs headless in tests, in Pyodide, or on a server."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable
from .planet import Planet
from .rover import RoverSpec, MODES

DT_S = 60.0           # physics step
CONTROL_DT_S = 300.0  # how often the student's controller runs


@dataclass
class Result:
    survived: bool
    sols_completed: float
    science_hours: float
    cause_of_failure: str | None
    log: list = field(default_factory=list)  # (t_s, battery_wh, internal_k, air_k, solar_w, mode, heater)


def run(controller: Callable[[dict], dict], planet: Planet | None = None,
        spec: RoverSpec | None = None, sols: float = 10.0, record_every_s: float = 600.0) -> Result:
    planet = planet or Planet.load("mars_gale")
    spec = spec or RoverSpec()
    batt = spec.battery_capacity_wh * spec.start_battery_frac
    t_int = spec.start_internal_temp_k
    t, science_s = 0.0, 0.0
    mode, heater = "sleep", False
    t_end = sols * planet.sol_seconds
    log, next_log, next_ctrl = [], 0.0, 0.0

    while t < t_end:
        air = planet.air_temp_k(t)
        solar_w = planet.solar_flux_w_m2(t) * spec.panel_area_m2 * spec.panel_efficiency

        if t >= next_ctrl:
            state = {
                "sol": planet.sol(t), "local_hour": planet.local_hour(t),
                "battery_wh": batt, "battery_pct": 100 * batt / spec.battery_capacity_wh,
                "internal_temp_c": t_int - 273.15, "air_temp_c": air - 273.15,
                "solar_w": solar_w, "dust_tau": planet.dust_tau(t),
                "pressure_pa": planet.surface_pressure_pa,
            }
            try:
                act = controller(state) or {}
            except Exception as exc:  # student bugs are part of the game
                return Result(False, planet.sol(t), science_s / 3600, f"controller crashed: {exc!r}", log)
            mode = act.get("mode", "sleep") if act.get("mode") in MODES else "sleep"
            heater = bool(act.get("heater", False))
            next_ctrl += CONTROL_DT_S

        powered = batt > 0.0
        load_w = (MODES[mode] + (spec.heater_power_w if heater else 0.0)) if powered else 0.0
        batt = min(spec.battery_capacity_wh, max(0.0, batt + (solar_w - load_w) * DT_S / 3600.0))
        heat_in = (MODES[mode] + (spec.heater_power_w if heater else 0.0)) if powered else 0.0
        t_int += (heat_in - spec.insulation_w_per_k * (t_int - air)) * DT_S / spec.thermal_mass_j_per_k
        if powered and mode == "science":
            science_s += DT_S

        if t >= next_log:
            log.append((t, batt, t_int, air, solar_w, mode, heater))
            next_log += record_every_s
        t += DT_S
        if t_int < spec.min_survival_temp_k:
            return Result(False, planet.sol(t), science_s / 3600,
                          "frozen: internal temperature below survival limit", log)
    return Result(True, sols, science_s / 3600, None, log)
