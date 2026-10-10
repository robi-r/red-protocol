# Design notes
- Physics step 60 s, controller step 300 s. Student code runs on the slower clock like real flight software.
- Student exceptions end the mission with a readable message, not a stack trace crash.
- Determinism: no randomness in v0.1, so results are reproducible and testable.
- Planet = frozen dataclass loaded from JSON. Environment functions are pure functions of time.
