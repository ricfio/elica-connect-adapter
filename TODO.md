# Elica Connect HA - TODO

## Architettura e Layer

- [x] Verificare il disaccoppiamento framework-agnostic dei moduli in `core/`, `domain/` e `adapters/`
- [ ] Consolidare i modelli in `domain/` (validazione dati da API/MQTT)

## Resilienza e Gestione Errori

- [ ] Ottimizzare riconnessione e backoff esponenziale in MQTT (`mqtt_client_aiomqtt.py`)
- [ ] Gestire granularmente le eccezioni in Config Flow e Coordinator (`ConfigEntryNotReady`, `InvalidAuth`, ecc.)

## Testing e CI/CD

- [ ] Espandere copertura test per `coordinator.py`, piattaforme (Fan/Light/Switch) e adapter
- [x] Configurare e verificare linting e tipizzazione statica (mypy, ruff)
- [x] Configurare CI GitHub Actions per linting e tipizzazione

## Home Assistant & Best Practices

- [ ] Pianificare avanzamento Quality Scale (da Bronze verso Silver/Gold)
- [x] Garantire la pulizia corretta delle risorse (sottoscrizioni MQTT, sessioni REST) alla rimozione dell’entry

## Release 0.2.0 review

- [x] Isolare i token in memoria per config entry.
- [x] Evitare payload MQTT completi nei log.
- [x] Usare timestamp UTC timezone-aware.
- [x] Verificare con Elica la modalità TLS/porta del broker MQTT prima della release.
- [x] Aggiungere test per più config entry e autenticazione isolata.

## Manutenzione e Codice

- [ ] Abilitare i controlli interattivi (Number e Switch) per il timer di spegnimento automatico (Capability 432 / FAN_SHUTOFF_TIMER) non appena validata la chiamata API di set/stop
