# Changelog

All notable changes to this project will be documented in this file.

## [0.2.5] - 2026-11-13

### Changed

- Documented the independent project history, related Elica Connect
  integrations, license, and project disclaimer.

## [0.2.4] - 2026-11-13

### Fixed

- Corrected manifest key ordering for Hassfest validation.
- Added a version bump helper for release metadata.

## [0.2.3] - 2026-11-13

### Fixed

- Updated the manifest and setup schema for current Home Assistant validation.

### Changed

- Added MIT license, integration categories, local brand assets, and HACS/Hassfest validation workflows.

## [0.2.2] - 2026-11-13

### Changed

- Improved the README with a visible screenshot gallery and clearer installation guidance.
- Added community promotion materials, contribution guidance, and structured issue templates.
- Documented the verified Elica BOXIN ADV PLUS IX/A/90 device and supported features.

## [0.2.1] - 2026-11-13

### Changed

- Improved README installation, configuration, requirements, and troubleshooting guidance.
- Added direct My Home Assistant links for HACS installation and config flow setup.

## [0.2.0] - 2026-11-12

### Changed

- Consolidated the integration for a preparatory release before `1.0.0`.
- Updated repository guidance, release metadata, and automated quality checks.

### Security

- Removed the personal development token from the devcontainer configuration.
- Enabled TLS for MQTT connections using the broker's secure port (`8883`).

## [0.1.0] - 2026-10-24

### Added

- **Fan Platform**: 4-speed hybrid mapping with bidirectional boost sync, preset modes, and robust percentage/speed calculations.
- **Light Platform**: Full light control supporting brightness adjustments, string-normalized dataModel keys, and optimistic locking.
- **Switch Platform**: Added `ElicaBoostSwitch` and `ElicaAirmaticSwitch` for Boost and Airmatic mode control.
- **Sensor Platform**: Added Device Details sensor, Grease Filter Efficiency sensor, Fan Shut-off Timer sensor, connectivity sensors, and MQTT message statistics.
- **API & MQTT Integration**: Robust REST API client with persistent HTTP connections and cached `products.json`; secure MQTT client supporting QoS 1, strict TLS validation, and retained message handling.
- **Optimistic Locking**: Implemented robust lock grace periods (`_get_lock_until`) to ignore stale MQTT echoes after user commands.

### Changed

- **Coordinator**: Enforced immutable state updates and improved coordinator resilience and error handling.
- **Code Quality**: Modernized code quality checks with strict Ruff linting, formatting, and Mypy static type checking (zero errors).

### Fixed

- Fan speed percentage computing and turn-on fallback behavior when speed is zero.
- MQTT listener cleanup upon config entry unloading.
