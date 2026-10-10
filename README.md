# Red Protocol

**Write the code. Survive the planet.**

Red Protocol teaches programming through survival. A student writes the control logic for a solar-powered
rover on Mars. The planet's real conditions (dust opacity, temperature swings, a 24.6-hour sol, solar flux)
decide whether the code lives or dies.

Built for the NASA Space Apps Challenge 2026, challenge: **Space Mission Design Game**
(*verify against the official statement released Oct 28, 2026*).

## Try it in 30 seconds

```bash
git clone <this-repo> && cd red-protocol
pip install -e . pytest
redprotocol examples/naive_controller.py       # LOST at sol 8.14: frozen
redprotocol examples/survivor_controller.py    # SURVIVED
pytest
```

Mission 1 is a 10-sol run through a regional dust storm. The naive controller (always do science, heater on)
drains the battery and freezes. The reference controller reads the sensors and adapts. Students write their
own `controller(state) -> {"mode", "heater"}` and compare.

## What the student sees

```python
def controller(state):
    # state: sol, local_hour, battery_pct, internal_temp_c, air_temp_c,
    #        solar_w, dust_tau, pressure_pa
    if state["dust_tau"] > 2 or state["battery_pct"] < 50:
        return {"mode": "sleep", "heater": state["internal_temp_c"] < -35}
    return {"mode": "science", "heater": state["internal_temp_c"] < -30}
```

## Architecture

```
src/redprotocol/
  planet.py   environment model (time -> temperature, dust, sunlight). Data driven.
  rover.py    hardware spec and action vocabulary
  sim.py      headless simulation engine (pure Python, no dependencies)
  data/       one JSON file per planet. Adding Venus or Titan = adding a file.
examples/     naive and reference controllers
tests/        physics and gameplay tests
```

The engine has no UI code, so it runs in tests, on a server, or in the browser via Pyodide (planned).

## Data sources

- NASA Planetary Fact Sheet (Mars): gravity, mean surface pressure, sol length
- Curiosity REMS (PDS Atmospheres node): air temperature and pressure for calibration and validation
- Mars Climate Database: dust opacity scenarios

## Honest limitations (v0.1)

- Temperature and dust parameters are **placeholders** and are not yet calibrated against REMS data.
  Validation chart (simulated vs measured) is the first milestone for the hackathon.
- Solar model is simplified: fixed equinox geometry, Beer-Lambert direct beam plus a crude diffuse term.
- Thermal model is a single lumped mass. Real rovers are far more complex.
- One planet (Mars, Gale Crater) and one mission so far.

## Roadmap

1. REMS validation chart and calibrated parameters
2. Browser UI with in-page code editor (Pyodide) and live telemetry plots
3. Missions 2-4: power budgeting, driving and terrain, communication delay
4. AI tutor that explains failures and gives hints (optional, never required to play)
5. Venus and Titan as new data files
6. Teacher dashboard

## License

MIT
