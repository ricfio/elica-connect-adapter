# Elica Connect - Custom Component for Home Assistant

## Sensors Documentation

This integration provides a comprehensive set of entities and sensors for Elica connected devices (hoods and appliances), divided into connectivity, capability telemetry, and MQTT diagnostics.

### 1. Connectivity Sensor
- **Entity Name:** Connectivity (`connectivity`)
- **Category:** Diagnostic (`SensorDeviceClass.ENUM`)
- **States:** `connected`, `disconnected`
- **Description:** Monitors whether the device is currently connected to the Elica cloud / network service based on the device's connection status.

### 2. Capability Sensors
Elica devices communicate via numerical capability codes reported in the device's data model. The integration maps these capabilities to dedicated sensors and climate/fan/light entities:

| Code | Description | Type | Unit | HA Mapping |
| ---: | :--- | :---: | :---: | :--- |
| **64** | Fan Mode (bitmask) | int | - | Fan Entity & Sensor |
| **69** | Fan Boost Timer (remaining) | int | min | Sensor (`Duration`) |
| **96** | Light Brightness | int | % | Light Entity & Sensor |
| **110** | Fan Speed | int | - | Fan Entity & Sensor |
| **128** | Grease Filter Saturation / Efficiency | int | % | Diagnostic Sensor (`PERCENTAGE`) |

#### Detailed Capability Breakdown:
- **Fan Mode (`64`):** Bitmask representing operational flags (`0` = Off, `1` = Fan active, `4` = Intensive mode active, `32` = Airmatic mode active).
- **Boost Timer (`69`):** Remaining countdown time in minutes for intensive boost mode.
- **Light Brightness (`96`):** Current brightness percentage of the hood lights (`0–100%`).
- **Fan Speed (`110`):** Current fan speed level (`0–3`).
- **Grease Filter Efficiency (`128`):** Reports filter wear level and efficiency (`100 - saturation`). Includes extra state attributes detailing filter ID, type, status, saturation alert, installation date, and last reset.

### 3. MQTT Diagnostic Sensors
- **MQTT State (`mqtt_state`):**
  - **Class:** Diagnostic (`SensorDeviceClass.ENUM`)
  - **States:** `connected`, `disconnected`
  - **Attributes:** Broker URL, client ID (`eiot-app`), last connection timestamp, last disconnection timestamp.
- **MQTT Messages (`mqtt_messages`):**
  - **Class:** Diagnostic (`SensorStateClass.TOTAL_INCREASING`)
  - **Description:** Total number of received MQTT telemetry messages.
  - **Attributes:** Last message timestamp, last message payload.

---

## Appendix

### Device Capabilities Reference Table

|    Code | Description                 | Type  | Unit | Constraints | Observed Values | HA Mapping          |
| ------: | :-------------------------- | :---: | :--: | :---------: | :-------------: | :------------------ |
|   **5** |                             |       |      |             | 0               |                     |
|   **6** |                             |       |      |             | 0               |                     |
|  **64** | Fan Mode (bitmask)          | int   |      |             | 0, 1, 5, 32     | Fan Entity          |
|  **68** |                             |       |      |             | 0               |                     |
|  **69** | Fan Boost Timer (remaining) | int   | min  | 5-0         | 5..0 (minutes)  | Sensor (Duration)   |
|  **71** |                             |       |      |             | 0               |                     |
|  **72** |                             |       |      |             | 1               |                     |
|  **96** | Light Brightness            | int   | %    | 0-100       | 0..100          | Light Entity        |
| **110** | Fan Speed                   | int   |      | 0-3         | 0               | Fan Entity          |
| **112** |                             |       |      |             | -               | None                |
| **128** | Grease Filter Saturation    | int   | %    | 0-100       | 0..100 (%)      | Sensor (Diagnostic) |
| **129** |                             |       |      |             | 0               |                     |
| **131** |                             |       |      |             | 1               |                     |

*Note:*  
*Capability rows without description and mapping are reserved / unmapped slots observed in device telemetry.*
