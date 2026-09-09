# Elica Connect - Home Assistant Custom Component

## Project Overview

Home Assistant custom component for Elica connected appliances (hoods and connected devices). Integrates via REST API and MQTT (`aiomqtt`).

## Architecture & Codebase Structure

- **`custom_components/elica_connect_adapter/`**: Core Home Assistant integration code:
  - `config_flow.py`: UI configuration flow.
  - `coordinator.py`: `DataUpdateCoordinator` for polling and state coordination.
  - `api/`: REST API communication and authentication.
  - `fan.py`, `light.py`, `sensor.py`, `switch.py`: Home Assistant entity platforms.
  - `sensors/`: Modular sensor definitions (mqtt sensors, capability sensors, miscellaneous sensors).
  - `manufaturer/`: Product specifications and metadata (`products.json`).
- **`tests/`**: Test suite using pytest.

## Developer Workflow & Commands

- **Run tests**:

  ```bash
  make test
  # or: pytest --cov=custom_components/elica_connect_adapter tests/ -v
  ```

- **Linting & Code Quality**:

  ```bash
  make lint
  ```

- **Install dependencies**:

  ```bash
  make install
  ```

## Coding Guidelines

- **Async/Await**: All network I/O and HA operations must be asynchronous.
- **Error Handling**: Raise appropriate HA exceptions (`ConfigEntryNotReady`, `InvalidAuth`, `CannotConnect`) during setup and config flow.
- **Code Quality**: Follow Home Assistant standards, Black formatting, isort import sorting, and pylint rules.
