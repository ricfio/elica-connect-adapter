# Elica Connect – Agent Guide

## Scope

This repository contains the Home Assistant custom integration
`elica_connect_adapter`. Keep Home Assistant-specific code in
`custom_components/elica_connect_adapter/`; the API package located at
`custom_components/elica_connect_adapter/api/` is deliberately kept independent
so it can later move to its own repository.

## Working rules

- Make focused, backwards-compatible changes. Preserve unrelated working-tree
  changes.
- Use asynchronous APIs for network and Home Assistant I/O.
- Do not run `git commit`; upon completing any requested implementation task, always propose a structured git commit message summarizing the changes.
- Keep comments and identifiers in English.
- Be concise.
- Update `strings.json`, `translations/en.json`, and `translations/it.json`
  together whenever user-visible configuration text changes.
- Do not change `PLATFORMS` without also handling platform setup and unload.
- Commenting and Documentation:
  - Keep comments concise and informative.
  - Module-level docstrings should be brief.
  - Class docstrings should use a concise noun phrase (e.g., "Elica sensor base class").
  - Avoid redundant docstrings for `__init__` methods unless they provide non-obvious context.
  - Commit messages must not include information about the AI agent that contributed.

## Architecture

- `__init__.py`: integration setup, coordinator and platform forwarding.
- `config_flow.py`: configuration and options flow handlers.
- `coordinator.py`: polling, MQTT lifecycle, and shared device state.
- `entity.py`: base entity definitions.
- `fan.py`, `light.py`, `number.py`, `sensor.py`, `switch.py`: coordinator-backed entities.
- `sensors/`: specialized sensor implementations.
- `api/`: API client, auth, domain models, interfaces, and adapters (`custom_components/elica_connect_adapter/api/`). Avoid importing Home Assistant modules from API domain/core/interface code.
- `const.py`, `utils.py`: constants and shared utility helpers.

## Entity conventions

- Use `CoordinatorEntity` for coordinator-backed entities.
- Device identifiers use `(DOMAIN, device.id)`.
- Entity unique IDs follow `elica_{device.id}_{kind}`.
- After a successful command, request a coordinator refresh before writing
  entity state.

## Validation & Code Quality

Run the narrowest relevant check first, then the complete suite before handing
off a substantial change:

```bash
make test    # Runs pytest with coverage
make lint    # Runs black, isort, and pylint
```

Additionally, static typing and linting rules are configured via `mypy` and `ruff` (`pyproject.toml`).
Use `make init` to create the development environment and install dependencies (`requirements_test.txt`).
Keep test additions deterministic; mock external REST and MQTT traffic.
