import importlib.util, pathlib
from redprotocol import Planet, run

EX = pathlib.Path(__file__).parent.parent / "examples"

def load(name):
    s = importlib.util.spec_from_file_location(name, EX / name)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m.controller

def test_mars_constants():
    p = Planet.load()
    assert abs(p.gravity_m_s2 - 3.71) < 0.01
    assert abs(p.sol_seconds - 88775) < 1

def test_no_sunlight_at_midnight():
    p = Planet.load()
    assert p.solar_flux_w_m2(0.0) == 0.0

def test_dust_reduces_solar():
    p = Planet.load()
    noon_clear = 0.5 * p.sol_seconds                  # sol 0.5, no storm
    noon_storm = 3.5 * p.sol_seconds                  # sol 3.5, storm
    assert p.solar_flux_w_m2(noon_storm) < 0.2 * p.solar_flux_w_m2(noon_clear)

def test_temperature_bounds_clear_day():
    p = Planet.load()
    temps = [p.air_temp_k(h * 3600) for h in range(0, 24)]
    assert 175 < min(temps) < 190 and 260 < max(temps) < 275

def test_naive_controller_dies_in_storm():
    r = run(load("naive_controller.py"))
    assert not r.survived

def test_survivor_controller_lives_and_does_science():
    r = run(load("survivor_controller.py"))
    assert r.survived and r.science_hours > 20

def test_battery_stays_in_bounds():
    r = run(load("survivor_controller.py"))
    assert all(0.0 <= row[1] <= 1200.0 for row in r.log)

def test_deterministic():
    a = run(load("survivor_controller.py")); b = run(load("survivor_controller.py"))
    assert a.science_hours == b.science_hours

def test_buggy_controller_is_reported_not_raised():
    r = run(lambda s: 1 / 0)
    assert not r.survived and "crashed" in r.cause_of_failure
