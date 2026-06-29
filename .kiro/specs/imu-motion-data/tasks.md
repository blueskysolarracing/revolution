# Implementation Plan: IMU Motion Data

## Overview

This plan extends the Miscellaneous orientation worker to capture angular
velocity and linear acceleration (already available in `OperationMode.IMU`) and
to derive angular acceleration in software via numerical differentiation. Work
proceeds bottom-up: first the shared `Contexts` data model and its instantiation
sites so everything constructs cleanly, then the pure `derive_angular_acceleration`
helper, then the worker loop that wires reads, derivation, state management, and
publishing together. Optional telemetry exposure and a final checkpoint close
out the plan. Each step builds on the previous one with no orphaned code.

## Tasks

- [x] 1. Extend the Contexts data model with the new motion fields
  - In `revolution/environment.py`, add three `dict[str, float]` fields to the
    `Contexts` dataclass immediately after `miscellaneous_orientation`:
    `miscellaneous_angular_velocity`, `miscellaneous_linear_acceleration`,
    `miscellaneous_angular_acceleration`.
  - Keep them above `miscellaneous_orientation_imu_working` to match the design.
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 2. Update Contexts instantiation sites with empty-dict defaults
  - [x] 2.1 Update root `configurations.py`
    - Add `miscellaneous_angular_velocity={}`,
      `miscellaneous_linear_acceleration={}`,
      `miscellaneous_angular_acceleration={}` immediately after
      `miscellaneous_orientation={}`.
    - _Requirements: 7.1, 7.3_

  - [x] 2.2 Update `revolution/tests/configurations.py`
    - Add the same three empty-dict defaults immediately after
      `miscellaneous_orientation={}`.
    - _Requirements: 7.2, 7.3_

- [x] 3. Checkpoint - Contexts constructs cleanly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement the angular-acceleration derivation helper
  - [x] 4.1 Add `derive_angular_acceleration()` to `revolution/miscellaneous.py`
    - Signature:
      `derive_angular_acceleration(current: dict[str, float], previous: dict[str, float] | None, dt: float) -> dict[str, float]`.
    - Return `{"x": 0.0, "y": 0.0, "z": 0.0}` when `previous is None` or `dt == 0`.
    - Otherwise return `{k: (current[k] - previous[k]) / dt for k in ("x","y","z")}`.
    - Do not mutate `current` or `previous`.
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [ ]* 4.2 Write property test for differentiation correctness
    - **Property 3 (P3): differentiation correctness** — for consecutive samples
      with `dt > 0`, each axis equals `(av[axis] - av_prev[axis]) / dt`.
    - Use Hypothesis to generate random current/previous vectors and `dt > 0`.
    - **Validates: Requirements 2.1**

  - [ ]* 4.3 Write property test for input immutability
    - **Property 5 (P5): input immutability** — `derive_angular_acceleration`
      leaves `current` and `previous` unmodified over random inputs.
    - **Validates: Requirements 2.5**

  - [ ]* 4.4 Write unit tests for derivation edge cases
    - First sample (`previous=None`) returns zeros; `dt == 0` returns zeros;
      negative-delta values; result always has keys `"x"`, `"y"`, `"z"`.
    - **Property 2 (P2): first-sample safety** is exercised at the `previous=None`
      boundary.
    - _Requirements: 2.2, 2.3, 2.4_

- [x] 5. Modify the `_orientation()` worker to read, derive, and publish motion data
  - [x] 5.1 Read angular velocity and linear acceleration each successful iteration
    - In the working branch, read `angular_velocity` and `linear_acceleration`
      from the BNO055 periphery and convert each `Vector` via
      `dataclasses.asdict` into a `{"x","y","z"}` dict.
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 5.2 Maintain and reset previous-sample state with monotonic timestamps
    - Introduce `previous_angular_velocity` and `previous_timestamp` worker-local
      state initialized to `None`.
    - Capture `time.monotonic()` on each successful read; compute
      `dt = now - previous_timestamp` when a baseline exists.
    - On `I2CError`, reset both `previous_angular_velocity` and
      `previous_timestamp` to `None` so no derivative spans an outage.
    - After a successful read, store the read angular velocity and timestamp as
      the new baseline.
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 5.3 Derive and publish all four motion fields
    - Call `derive_angular_acceleration(angular_velocity, previous_angular_velocity, dt)`;
      first successful sample after start or recovery yields zeros.
    - Within a `contexts()` block, `update()` `miscellaneous_orientation`,
      `miscellaneous_angular_velocity`, `miscellaneous_linear_acceleration`, and
      `miscellaneous_angular_acceleration`, and set
      `miscellaneous_orientation_imu_working` to reflect the last operation.
    - _Requirements: 3.1, 3.2, 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 5.4 Confirm `imu_config()` and recovery path remain unchanged
    - Leave the `imu_config()` sequence (`reset2()` → config-mode write →
      `select_units(MS2, DPS, DEGREES, CELSIUS)` → `OperationMode.IMU`) intact;
      keep the not-working branch reconfiguring before resuming reads.
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [ ]* 5.5 Write property tests for the worker derivative lifecycle
    - **Property 2 (P2): first-sample safety** — first successful read after
      start/recovery publishes zero angular acceleration.
    - **Property 4 (P4): no stale derivative** — after an `I2CError`, the next
      successful sample is treated as a first sample (state invalidated).
    - Use Hypothesis to drive sequences of mocked reads interleaved with
      `I2CError` injections.
    - **Validates: Requirements 3.1, 3.2, 4.3**

  - [ ]* 5.6 Write unit tests for the worker with a mocked BNO055
    - Mock the periphery to return known `Vector`s; assert all four context
      fields are populated and `imu_working` transitions correctly
      (**P1: availability**).
    - Inject `I2CError` and assert previous-sample state resets and the next read
      produces zero acceleration; assert `imu_config()` sequence unchanged
      (**P6: config invariance**).
    - _Requirements: 1.1, 1.2, 1.3, 4.3, 5.5, 8.1, 8.2, 8.3, 8.4_

- [x] 6. Checkpoint - worker reads, derives, and publishes correctly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. (Optional) Expose new motion fields in telemetry
  - [ ]* 7.1 Add the three fields to the Telemetry `Data` dataclass
    - In `revolution/telemetry.py`, add `miscellaneous_angular_velocity`,
      `miscellaneous_linear_acceleration`, and `miscellaneous_angular_acceleration`
      typed as `dict[str, float]` near `miscellaneous_orientation`, and populate
      them from `Contexts` where the `Data` instance is built.
    - _Requirements: 9.1_

- [x] 8. Final checkpoint - full verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional (tests and optional telemetry) and can be
  skipped for a faster MVP; core implementation tasks are never optional.
- Each task references specific requirement clauses for traceability.
- Property-based tests (Hypothesis) validate the universal correctness properties
  P1–P6 from the design; unit tests cover specific examples and edge cases.
- Checkpoints provide incremental validation at natural breaks.
