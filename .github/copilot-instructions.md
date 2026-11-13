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
- Treat the Elica mobile-app client credential as an application credential; never add user tokens or passwords.
- Never log access tokens, MQTT credentials, or complete MQTT payloads.
- Keep authentication state isolated per Home Assistant config entry.
- Preserve the API package boundary; do not import Home Assistant from `api/core`, `api/domain`, or `api/interfaces`.
- Do not change MQTT transport settings without a compatibility test against the Elica broker.
- Do not create Git commits without explicit user confirmation; show the proposed message first.

## Release workflow

- Use Git Flow for releases: start with `git flow release start X.Y.Z` before
  release changes and finish with `git flow release finish X.Y.Z` after the
  confirmed commit.
- The repository uses the `v` tag prefix, so release `0.2.4` produces tag
  `v0.2.4`.
- Run `make bump-version VERSION=X.Y.Z` to update release metadata, then add
  the `CHANGELOG.md` entry manually.
- Run `make lint` and the relevant tests before proposing the release commit.
