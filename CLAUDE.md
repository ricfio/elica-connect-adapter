# Elica Connect - Home Assistant Custom Component

## Project Overview

Home Assistant custom component for Elica connected appliances (hoods and connected devices). Integrates via REST API and MQTT (`aiomqtt`). Integration domain: `elica_connect_adapter`.

## Architecture & Codebase Structure

- **`custom_components/elica_connect_adapter/`**: Core Home Assistant integration code:
  - `__init__.py`: Entry point setup (`async_setup_entry`), instantiates `Controller` and `ElicaConnectCoordinator`, stores them in `hass.data[DOMAIN][entry_id]`, and sets up platforms (`fan`, `light`, `sensor`, `switch`).
  - `config_flow.py`: UI configuration flow.
  - `coordinator.py`: `ElicaConnectCoordinator` (`DataUpdateCoordinator`) handling 60s device polling and MQTT real-time message listening. `coordinator.data` shape is `{"devices": {device_id: Device}, "mqtt_stats": {...}}`. Use `coordinator.get_device(device_id)` to retrieve devices.
  - `api/`: REST API communication, authentication (`api/core/auth/`, `api/core/controller.py`), domain models (`api/domain/`), and adapters (`api/adapters/cli/`, `api/adapters/ha/`, `api/adapters/shared/`).
  - `fan.py`, `light.py`, `sensor.py`, `switch.py`: Home Assistant entity platforms (subclassing `CoordinatorEntity`).
  - `sensors/`: Modular sensor definitions (capability sensors, mqtt sensors, miscellaneous sensors).
  - `manufaturer/`: Product specifications and metadata (`products.json`).
  - `translations/`: Localization files (`en.json`, `it.json`) and `strings.json`.
- **`tests/`**: Comprehensive test suite using pytest (`test_config_flow.py`, `test_sensor.py`, `conftest.py`).

## Key Patterns & Coding Conventions

- **Async/Await**: All network I/O and HA operations must be asynchronous.
- **Error Handling**: Raise appropriate HA exceptions (`ConfigEntryNotReady`, `InvalidAuth`, `CannotConnect`) during setup and config flow.
- **Unique IDs**: Formatted as `f"elica_{device.id}_<type>"` (e.g. `elica_123_fan`).
- **Device Identifiers**: `DeviceInfo(identifiers={(DOMAIN, self._device.id)})`.
- **Coordinator State Updates**: Subclass `CoordinatorEntity`. After commands, call `await coordinator.async_request_refresh()` and `self.async_write_ha_state()`.
- **Controller API**: Methods (e.g. `set_fan_mode`, `set_light_brightness`, `toggle_light`) return `True`/`False` for acceptance/rejection or `None` on network errors (network errors wrapped via decorators). Falsy values indicate failure.
- **MQTT Integration**: Listens on topics matching `MQTT_TOPIC_FORMAT` (`"v1/device/{CUID}/statusjson"`). CUID is extracted via `topic.split('/')[-2]`.
- **Localization (i18n)**: Whenever adding config flow steps or UI strings, update `strings.json`, `translations/en.json`, and `translations/it.json`. Before committing, verify that any new strings or texts are included in all translation files and ensure they are correct and consistent.
- **Code Quality**: Follow Home Assistant standards, Black formatting, isort import sorting, pylint rules. Code comments must be in English. Do not modify `PLATFORMS` in `__init__.py` without handling platform forwarding and unloading.

## Developer Workflow & Commands

### Initialize Environment

```bash
make init
```

### Run Tests

```bash
make test
# $(VENV_PATH)/bin/pytest --cov=custom_components/elica_connect_adapter tests/ -v
```

**Important**: Always run and verify that all automated tests pass successfully before making any commit. Test dependencies and environment setup are managed via `requirements_test.txt` and the `Makefile` (`make init` / `make install`).

### Linting & Code Quality

```bash
make lint
```

### Install Dependencies

```bash
make install
```

### Clean Build Artifacts

```bash
make clean
```

### Committing Changes

**Important**: Never execute the `git commit` command. Instead, suggest a commit message to the user, and they will perform the commit themselves.
