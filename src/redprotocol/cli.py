import argparse, importlib.util
from .sim import run


def main():
    p = argparse.ArgumentParser(description="Run a controller on Mars.")
    p.add_argument("controller", help="path to a .py file defining controller(state) -> dict")
    p.add_argument("--sols", type=float, default=10)
    a = p.parse_args()
    spec = importlib.util.spec_from_file_location("student", a.controller)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    r = run(mod.controller, sols=a.sols)
    status = "SURVIVED" if r.survived else f"LOST at sol {r.sols_completed:.2f}: {r.cause_of_failure}"
    print(f"{status} | science hours: {r.science_hours:.1f}")


if __name__ == "__main__":
    main()
