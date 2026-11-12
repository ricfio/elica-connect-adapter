# Elica Connect contribution guide

- Keep Home Assistant integration code under `custom_components/elica_connect_adapter/`.
- Keep `custom_components/elica_connect_adapter/api/` independent from Home Assistant imports.
- Preserve asynchronous I/O and coordinator-backed entity patterns.
- Use device identifiers `(DOMAIN, device.id)` and unique IDs `elica_{device.id}_{kind}`.
- After successful commands, refresh the coordinator before updating entity state.
- Update `strings.json`, `translations/en.json`, and `translations/it.json` together for UI text changes.
- Add deterministic tests for behavior changes; mock REST and MQTT traffic.
- Run `make lint` and the relevant pytest tests before handoff.
- Do not commit credentials, personal data, generated caches, or local prompts.
