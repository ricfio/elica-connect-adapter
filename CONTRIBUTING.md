# Contributing to Elica Connect

Thank you for helping improve this community Home Assistant integration.

## Bug reports and compatibility

Use the GitHub issue templates and include the integration version, Home
Assistant version, Elica model, expected behavior, and sanitized logs. Remove
passwords, access tokens, serial numbers, account identifiers, and complete MQTT
payloads before posting.

## Development checks

Install the test dependencies and run:

```bash
make lint
make test
```

Mock REST and MQTT traffic in tests. Keep the API package independent from Home
Assistant imports and preserve asynchronous I/O.

## Release process

Releases use Semantic Versioning and annotated `vX.Y.Z` tags. Update the
manifest, `pyproject.toml`, and `CHANGELOG.md` together. Do not commit user
credentials or personal data.
