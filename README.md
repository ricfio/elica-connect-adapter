# Elica Connect - Custom Component for Home Assistant

## Appendix

### Device Capabilities

Elica hoods communicate via a set of numerical capability codes reported in the device's data model.  
The table below lists all known capabilities, their data types, units, constraints, observed values, and how they map to Home Assistant entities.

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
| **112** |                             |       |      |             | -               |                     |
| **128** | Grease Filter Saturation    | int   | %    | 0-100       | 0..100 (%)      | Sensor (Diagnostic) |
| **129** |                             |       |      |             | 0               |                     |
| **131** |                             |       |      |             | 1               |                     |

*Note:*  
*Capability rows without description and mapping are reserved / unmapped slots observed in device telemetry.*

#### 1. Fan Mode Bitmask (`64`)

The fan mode value is a bitmask representing active operational flags:
-  `0` (`00000000`) = Off
-  `1` (`00000001`) = Fan active
-  `4` (`00000100`) = Intensive mode active
- `32` (`00100000`) = Airmatic mode active

#### 2. Fan Boost Timer (`69`)

Represents the remaining countdown time in minutes for intensive mode (`5` to `0` minutes).

#### 3. Grease Filter Saturation (`128`)

Reports filter wear level (`0–100%`).  
In Home Assistant, this is exposed as a diagnostic sensor representing grease filter efficiency (`100 - saturation`).
