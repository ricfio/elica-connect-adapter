# Elica Connect – Agent Guide

## Scope

This repository contains the Home Assistant custom integration
`elica_connect_adapter`. Keep Home Assistant-specific code in
`custom_components/elica_connect_adapter/`; the `api/` package is deliberately
kept independent so it can later move to its own repository.

## Working rules

- Make focused, backwards-compatible changes. Preserve unrelated working-tree
  changes.
- Use asynchronous APIs for network and Home Assistant I/O.
- Do not run `git commit`; propose a commit message instead.
- Keep comments and identifiers in English.
- Update `strings.json`, `translations/en.json`, and `translations/it.json`
  together whenever user-visible configuration text changes.
- Do not change `PLATFORMS` without also handling platform setup and unload.

## Architecture

- `__init__.py`: integration setup, coordinator and platform forwarding.
- `coordinator.py`: polling, MQTT lifecycle, and shared device state.
- `fan.py`, `light.py`, `sensor.py`, `switch.py`: coordinator-backed entities.
- `sensors/`: sensor implementations.
- `api/`: API client, auth, domain models, interfaces, and adapters. Avoid
  importing Home Assistant modules from API domain/core/interface code.

## Entity conventions

- Use `CoordinatorEntity` for coordinator-backed entities.
- Device identifiers use `(DOMAIN, device.id)`.
- Entity unique IDs follow `elica_{device.id}_{kind}`.
- After a successful command, request a coordinator refresh before writing
  entity state.

## Validation

Run the narrowest relevant check first, then the complete suite before handing
off a substantial change:

```bash
make test
make lint
```

Use `make init` to create the development environment. Keep test additions
deterministic; mock external REST and MQTT traffic.
