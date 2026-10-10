"""Planet model: environment as a function of time. Data-driven, so a new planet is a new JSON file."""
from __future__ import annotations
import json, math
from dataclasses import dataclass, field
from importlib import resources


@dataclass(frozen=True)
class DustEvent:
    name: str
    start_sol: float
    end_sol: float
    tau: float
    temp_amp_damping: float = 1.0


@dataclass(frozen=True)
class Planet:
    name: str
    gravity_m_s2: float
    surface_pressure_pa: float
    sol_seconds: float
    solar_irradiance_w_m2: float
    latitude_deg: float
    air_temp_mean_k: float
    air_temp_amplitude_k: float
    temp_peak_local_hour: float
    dust_tau_clear: float
    dust_events: tuple = field(default_factory=tuple)

    @classmethod
    def load(cls, name: str = "mars_gale") -> "Planet":
        text = resources.files("redprotocol.data").joinpath(f"{name}.json").read_text()
        d = json.loads(text)
        events = tuple(DustEvent(**e) for e in d["dust_events"])
        keys = ["name", "gravity_m_s2", "surface_pressure_pa", "sol_seconds",
                "solar_irradiance_w_m2", "latitude_deg", "air_temp_mean_k",
                "air_temp_amplitude_k", "temp_peak_local_hour", "dust_tau_clear"]
        return cls(dust_events=events, **{k: d[k] for k in keys})

    # --- time helpers
    def sol(self, t_s: float) -> float:
        return t_s / self.sol_seconds

    def local_hour(self, t_s: float) -> float:
        """Local solar hour 0-24 (24 'Mars hours' per sol)."""
        return (t_s % self.sol_seconds) / self.sol_seconds * 24.0

    # --- environment
    def _active_event(self, t_s: float):
        s = self.sol(t_s)
        for e in self.dust_events:
            if e.start_sol <= s < e.end_sol:
                return e
        return None

    def dust_tau(self, t_s: float) -> float:
        e = self._active_event(t_s)
        return e.tau if e else self.dust_tau_clear

    def cos_zenith(self, t_s: float) -> float:
        """Sun elevation cosine; declination fixed at 0 (equinox) in this version."""
        h = (self.local_hour(t_s) - 12.0) / 24.0 * 2 * math.pi
        c = math.cos(math.radians(self.latitude_deg)) * math.cos(h)
        return max(0.0, c)

    def air_temp_k(self, t_s: float) -> float:
        e = self._active_event(t_s)
        amp = self.air_temp_amplitude_k * (e.temp_amp_damping if e else 1.0)
        phase = (self.local_hour(t_s) - self.temp_peak_local_hour) / 24.0 * 2 * math.pi
        return self.air_temp_mean_k + amp * math.cos(phase)

    def solar_flux_w_m2(self, t_s: float) -> float:
        """Surface flux on a horizontal panel: direct beam attenuated by dust (Beer-Lambert)
        plus a simple diffuse term that matters in storms. Simplified, documented in docs/."""
        c = self.cos_zenith(t_s)
        if c <= 0.0:
            return 0.0
        tau = self.dust_tau(t_s)
        direct = math.exp(-tau / max(c, 0.2))
        diffuse = 0.25 * (1 - math.exp(-tau)) * math.exp(-0.3 * tau)
        return self.solar_irradiance_w_m2 * c * (direct + diffuse * 1.0)
