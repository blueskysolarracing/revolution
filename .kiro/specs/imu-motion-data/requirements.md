# Requirements Document

## Introduction

This feature extends the Miscellaneous application's orientation worker
(`_orientation()` in `revolution/miscellaneous.py`) so that the BNO055 IMU
reports more than fused orientation. In its current `OperationMode.IMU` fusion
mode the BNO055 already exposes angular velocity (degrees per second) and
linear acceleration (gravity-removed, m/s²) alongside orientation, so these two
channels can be read without changing the IMU configuration. Angular
acceleration has no hardware register and is derived in software by numerically
differentiating angular velocity over measured elapsed time.

The feature adds three new motion fields to the shared `Contexts` data model,
publishes the readings each successful worker iteration, updates every
`Contexts` instantiation site with safe defaults, and preserves the existing
orientation behavior and `imu_config()` sequence unchanged.

## Glossary

- **Orientation_Worker**: The `_orientation()` worker loop in the Miscellaneous
  application that periodically reads the IMU and publishes motion data to
  `Contexts`.
- **IMU**: The BNO055 inertial measurement unit periphery, accessed as
  `peripheries.miscellaneous_orientation_imu_bno055`, configured in
  `OperationMode.IMU` fusion mode.
- **Contexts**: The shared mutable state dataclass defined in
  `revolution/environment.py` that workers read from and write to.
- **Angular_Velocity**: The gyroscope reading in degrees per second (dps),
  represented as a dict with keys `"x"`, `"y"`, `"z"`.
- **Linear_Acceleration**: The gravity-removed acceleration reading in m/s²,
  represented as a dict with keys `"x"`, `"y"`, `"z"`.
- **Angular_Acceleration**: The software-derived rate of change of
  Angular_Velocity in degrees per second squared (dps/s), represented as a dict
  with keys `"x"`, `"y"`, `"z"`.
- **Derive_Function**: The `derive_angular_acceleration()` helper that computes
  Angular_Acceleration from a current and previous Angular_Velocity sample and
  an elapsed time `dt`.
- **dt**: The elapsed time, measured with `time.monotonic()`, between two
  consecutive successful IMU reads.
- **Previous_Sample_State**: The retained `previous_angular_velocity` vector and
  `previous_timestamp` used as the baseline for differentiation.
- **imu_config**: The one-time IMU configuration routine inside
  `Orientation_Worker` (`reset2()` → config mode → `select_units(MS2, DPS,
  DEGREES, CELSIUS)` → `OperationMode.IMU`).
- **I2CError**: The exception raised by the periphery layer when an I2C
  operation with the IMU fails.

## Requirements

### Requirement 1: Read Angular Velocity and Linear Acceleration

**User Story:** As a telemetry consumer, I want the orientation worker to read
angular velocity and linear acceleration from the IMU, so that I have access to
the vehicle's rotational rate and gravity-removed acceleration.

#### Acceptance Criteria

1. WHEN the IMU is working and the Orientation_Worker completes an iteration read, THE Orientation_Worker SHALL read Angular_Velocity from the IMU `angular_velocity` property.
2. WHEN the IMU is working and the Orientation_Worker completes an iteration read, THE Orientation_Worker SHALL read Linear_Acceleration from the IMU `linear_acceleration` property.
3. WHEN the Orientation_Worker reads an IMU `Vector`, THE Orientation_Worker SHALL convert it to a dict with keys `"x"`, `"y"`, `"z"` using `dataclasses.asdict`.

### Requirement 2: Derive Angular Acceleration by Numerical Differentiation

**User Story:** As a telemetry consumer, I want angular acceleration computed in
software, so that I can observe rotational acceleration even though the IMU has
no register for it.

#### Acceptance Criteria

1. WHEN a previous Angular_Velocity sample exists AND dt is greater than 0, THE Derive_Function SHALL return, for each axis, `(current[axis] - previous[axis]) / dt`.
2. IF no previous Angular_Velocity sample exists, THEN THE Derive_Function SHALL return `{"x": 0.0, "y": 0.0, "z": 0.0}`.
3. IF dt equals 0, THEN THE Derive_Function SHALL return `{"x": 0.0, "y": 0.0, "z": 0.0}`.
4. THE Derive_Function SHALL return a dict with keys `"x"`, `"y"`, `"z"`.
5. THE Derive_Function SHALL leave its `current` and `previous` argument dicts unmodified.

### Requirement 3: First Successful Sample After Start or Recovery

**User Story:** As a system operator, I want the first reading after startup or
recovery to produce a safe angular acceleration value, so that no spurious
derivative is published when no baseline exists.

#### Acceptance Criteria

1. WHEN the Orientation_Worker produces the first successful sample after startup, THE Orientation_Worker SHALL publish Angular_Acceleration equal to `{"x": 0.0, "y": 0.0, "z": 0.0}`.
2. WHEN the Orientation_Worker produces the first successful sample after recovery from an I2CError, THE Orientation_Worker SHALL publish Angular_Acceleration equal to `{"x": 0.0, "y": 0.0, "z": 0.0}`.

### Requirement 4: Maintain and Reset Previous-Sample State

**User Story:** As a system operator, I want the worker to track and invalidate
its differentiation baseline correctly, so that angular acceleration is never
computed across an IMU outage.

#### Acceptance Criteria

1. WHEN the Orientation_Worker completes a successful read, THE Orientation_Worker SHALL store the read Angular_Velocity as `previous_angular_velocity` and the measured monotonic time as `previous_timestamp`.
2. WHILE `previous_angular_velocity` holds a value, THE Orientation_Worker SHALL keep `previous_timestamp` equal to the monotonic time of the sample stored in `previous_angular_velocity`.
3. IF an I2CError occurs during an IMU read, THEN THE Orientation_Worker SHALL reset `previous_angular_velocity` and `previous_timestamp` to `None`.
4. WHEN dt is computed for a successful sample, THE Orientation_Worker SHALL use the difference between the current monotonic time and `previous_timestamp`.

### Requirement 5: Publish Motion Data to Contexts

**User Story:** As a telemetry consumer, I want all four motion fields published
to Contexts each successful iteration, so that downstream workers can read
current motion data.

#### Acceptance Criteria

1. WHEN the Orientation_Worker completes a successful read, THE Orientation_Worker SHALL update `miscellaneous_orientation` in Contexts with the latest orientation reading.
2. WHEN the Orientation_Worker completes a successful read, THE Orientation_Worker SHALL update `miscellaneous_angular_velocity` in Contexts with the latest Angular_Velocity reading.
3. WHEN the Orientation_Worker completes a successful read, THE Orientation_Worker SHALL update `miscellaneous_linear_acceleration` in Contexts with the latest Linear_Acceleration reading.
4. WHEN the Orientation_Worker completes a successful read, THE Orientation_Worker SHALL update `miscellaneous_angular_acceleration` in Contexts with the derived Angular_Acceleration value.
5. WHEN the Orientation_Worker completes an iteration, THE Orientation_Worker SHALL set `miscellaneous_orientation_imu_working` in Contexts to reflect whether the last operation succeeded.

### Requirement 6: Extend the Contexts Data Model

**User Story:** As a developer, I want the new motion fields defined in the
shared data model, so that workers can read and write them consistently.

#### Acceptance Criteria

1. THE Contexts dataclass SHALL define `miscellaneous_angular_velocity` as a `dict[str, float]`.
2. THE Contexts dataclass SHALL define `miscellaneous_linear_acceleration` as a `dict[str, float]`.
3. THE Contexts dataclass SHALL define `miscellaneous_angular_acceleration` as a `dict[str, float]`.
4. THE Contexts dataclass SHALL declare the three new fields immediately after `miscellaneous_orientation`.

### Requirement 7: Update Contexts Instantiation Sites with Defaults

**User Story:** As a developer, I want every place that constructs Contexts to
supply defaults for the new fields, so that the application and tests construct
Contexts without error.

#### Acceptance Criteria

1. WHERE `Contexts` is constructed in `configurations.py`, THE construction SHALL supply a default empty dict for `miscellaneous_angular_velocity`, `miscellaneous_linear_acceleration`, and `miscellaneous_angular_acceleration`.
2. WHERE `Contexts` is constructed in `revolution/tests/configurations.py`, THE construction SHALL supply a default empty dict for `miscellaneous_angular_velocity`, `miscellaneous_linear_acceleration`, and `miscellaneous_angular_acceleration`.
3. WHEN the application or test suite constructs Contexts with the new fields defaulted, THE construction SHALL complete without raising a missing-argument error.

### Requirement 8: Preserve Existing Orientation Behavior and IMU Configuration

**User Story:** As a maintainer, I want the existing orientation behavior and
IMU configuration to remain unchanged, so that this feature adds data without
regressing current functionality.

#### Acceptance Criteria

1. THE imu_config routine SHALL retain the existing sequence: `reset2()`, then config-mode write, then `select_units(MS2, DPS, DEGREES, CELSIUS)`, then `OperationMode.IMU` write.
2. WHILE the IMU is operating, THE Orientation_Worker SHALL keep the IMU in `OperationMode.IMU`.
3. WHEN the IMU is not working at the start of an iteration, THE Orientation_Worker SHALL call imu_config to reconfigure the IMU before resuming reads.
4. WHEN the Orientation_Worker publishes orientation, THE Orientation_Worker SHALL continue to populate `miscellaneous_orientation` as it did before this feature.

### Requirement 9: Optional Telemetry Exposure

**User Story:** As a telemetry consumer, I want the option to transmit the new
motion fields over radio, so that motion data can be monitored remotely when the
added payload size is acceptable.

#### Acceptance Criteria

1. WHERE the new motion fields are added to the Telemetry `Data` dataclass, THE Telemetry `Data` dataclass SHALL include `miscellaneous_angular_velocity`, `miscellaneous_linear_acceleration`, and `miscellaneous_angular_acceleration` typed as `dict[str, float]`.
