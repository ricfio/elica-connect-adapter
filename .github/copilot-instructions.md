
## Elica Connect — Istruzioni per Copilot

Scopo: fornire a un agente AI (o a un nuovo contributore) le informazioni minime e operative per essere produttivo su questo custom component di Home Assistant.

- Dominio dell'integrazione: `elica_connect` (vedi `custom_components/elica_connect/const.py`).
- Piattaforme implementate: fan, light, switch (elencate in `custom_components/elica_connect/__init__.py` tramite `PLATFORMS`).

Panoramica (come si collega il tutto):
- `custom_components/elica_connect/__init__.py` — punti d'ingresso: `async_setup_entry` crea il `Controller` e l'`ElicaDataUpdateCoordinator`, li memorizza in `hass.data[DOMAIN][entry_id]` e inoltra il setup delle piattaforme.
- `connect/core/controller.py` — controller agnostico al framework che incapsula autenticazione, chiamate REST e l'avvio dell'ascolto MQTT. Gli errori di rete sono normalizzati dal decorator `handle_network_errors`.
- `coordinator.py` — `ElicaDataUpdateCoordinator` esegue il polling dei dispositivi ogni 60s e avvia l'ascolto MQTT via `Controller.listen(...)`. La forma di `coordinator.data` è `{"devices": {device_id: Device}}`; usa `get_device(device_id)` per recuperare un device.
- Le entità di piattaforma (es. `fan.py`, `light.py`) sono sottoclassi di `CoordinatorEntity` che leggono lo stato con `coordinator.get_device(...)` e inviano comandi tramite il `Controller`.

Pattern e esempi chiave (seguire esattamente):
- Unique ID: le entità usano il formato `f"elica_{device.id}_<type>"` (vedi `ElicaFan._attr_unique_id`).
- Identificatori dispositivo: usare `DeviceInfo(identifiers={(DOMAIN, self._device.id)})` — non cambiare questa semantica degli identificatori.
- Uso del coordinator: preferire `CoordinatorEntity`; dopo un comando che viene accettato, chiamare `await coordinator.async_request_refresh()` e aggiornare lo stato con `self.async_write_ha_state()`.
- API del controller: usare le API esistenti come `controller.set_fan_mode(...)`, `controller.set_light_brightness(...)`, `controller.toggle_light(...)` — restituiscono boolean (accepted) o `None` in caso di errore di rete.
- MQTT: il formato dei topic è `MQTT_TOPIC_FORMAT` in `connect/core/constants.py` ("v1/device/{CUID}/statusjson"). Il coordinator estrae il CUID con `topic.split('/')[-2]` e lo confronta con `device.cuid`.

Integrazione e effetti collaterali da considerare:
- Le credenziali MQTT e i token di autenticazione provengono dal provider in `connect/auth/*` — guardare anche `utils.create_controller` per capire come viene istanziato il controller dentro Home Assistant.
- Il `manifest.json` dichiara `config_flow: true` e `dependencies: ["mqtt"]` — i test del config flow si trovano in `tests/test_config_flow.py` e fanno mocking dell'autenticazione.

Testing e workflow di sviluppo (ricavabile dal repo):
- I test sono in `tests/` e usano i fixture pytest di Home Assistant (es. `HomeAssistant`, `mock_setup_entry`). Usare `tests/test_config_flow.py` come riferimento per i test del config flow.
- Esempio rapido per eseguire i test (l'ambiente richiede le dipendenze di test di Home Assistant):

```bash
pytest tests/test_config_flow.py -q
```

Regole piccole ma importanti per le modifiche:
- I commenti nel codice devono essere in inglese.
- Non modificare la lista `PLATFORMS` in `__init__.py` senza gestire il forwarding/unloading delle piattaforme.
- `coordinator.data` deve rimanere un dizionario con chiave `"devices"` che mappa a oggetti `Device`; il codice delle entità dipende da questa forma.
- Conservare la semantica dei metodi del controller: restituiscono `True`/`False` per accept/reject o `None` se il `handle_network_errors` intercetta un errore di rete — i chiamanti devono considerare valori falsy come fallimento.
- Quando si aggiungono stringhe per l'interfaccia utente o per il config flow, aggiornare `translations/en.json` e `strings.json` per mantenere coerenza.

Dove guardare per esempi nel repository:
- Setup e flow: `custom_components/elica_connect/__init__.py`
- Polling e integrazione MQTT: `custom_components/elica_connect/coordinator.py`
- Controller e logica di basso livello: `custom_components/elica_connect/connect/core/controller.py`
- Modelli di dominio e capability: `custom_components/elica_connect/connect/domain/*.py`
- Entità di piattaforma: `custom_components/elica_connect/fan.py`, `custom_components/elica_connect/light.py`, `custom_components/elica_connect/switch.py`
- Esempio di test: `tests/test_config_flow.py`

Se qualche sezione non è chiara o vuoi che espanda parti specifiche (per esempio: flusso di autenticazione, dettagli MQTT o template di test), dimmi quale parte e la approfondisco.

