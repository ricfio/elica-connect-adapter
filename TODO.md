# Elica Connect HA - TODO

## Architettura e Layer

- [ ] Verificare il disaccoppiamento framework-agnostic dei moduli in `core/`, `domain/` e `adapters/`
- [ ] Consolidare i modelli in `domain/` (validazione dati da API/MQTT)

## Resilienza e Gestione Errori

- [ ] Ottimizzare riconnessione e backoff esponenziale in MQTT (`mqtt_client_aiomqtt.py`)
- [ ] Gestire granularmente le eccezioni in Config Flow e Coordinator (`ConfigEntryNotReady`, `InvalidAuth`, ecc.)

## Testing e CI/CD

- [ ] Espandere copertura test per `coordinator.py`, piattaforme (Fan/Light/Switch) e adapter
- [ ] Configurare e verificare linting e tipizzazione statica (`mypy`, `ruff`, CI GitHub Actions)

## Home Assistant & Best Practices

- [ ] Pianificare avanzamento Quality Scale (da Bronze verso Silver/Gold)
- [ ] Garantire la pulizia corretta delle risorse (sottoscrizioni MQTT, sessioni REST) alla rimozione dell'entry

## Manutenzione e Codice

- [ ] Deduplicare le costanti condivise (es. CLIENT_SECRET, APP_UUID, API_BASE_URL) tra `const.py` e `api/core/constants.py`
- [ ] Implementare il lookup del nome prodotto da `manufacturer/products.json`
- [ ] Rimuovere file `.pyc` residui dalla working directory
- [ ] Completare internazionalizzazione i18n (`strings.json` e file di traduzione)
- [ ] Abilitare i controlli interattivi (Number e Switch) per il timer di spegnimento automatico (Capability 432 / FAN_SHUTOFF_TIMER) non appena validata la chiamata API di set/stop
