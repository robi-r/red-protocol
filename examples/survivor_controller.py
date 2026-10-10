"""Reference solution: read the sensors, protect the battery, heat only when needed."""
def controller(state):
    heater = state["internal_temp_c"] < -30
    if state["dust_tau"] > 2.0 or state["battery_pct"] < 50:
        return {"mode": "sleep", "heater": state["internal_temp_c"] < -35}
    return {"mode": "science", "heater": heater}
