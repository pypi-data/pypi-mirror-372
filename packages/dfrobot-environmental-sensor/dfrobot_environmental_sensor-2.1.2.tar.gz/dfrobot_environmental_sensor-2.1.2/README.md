# 🌍 DFRobot Environmental Sensor Library

![PyPI](https://img.shields.io/pypi/v/dfrobot-environmental-sensor)
![Python Version](https://img.shields.io/pypi/pyversions/dfrobot-environmental-sensor)
![License](https://img.shields.io/github/license/kallegrens/dfrobot-environmental-sensor)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

Python library for the multifunctional **DFRobot Environmental Sensor (SEN0500/SEN0501)**.

This sensor integrates **temperature 🌡️, humidity 💧, UV index ☀️, light intensity 💡, atmospheric pressure 🌪️, and altitude 🏔️** into one module.

It supports both **Gravity** and **Breakout** interfaces and communicates over **I²C** or **UART**.

> [!IMPORTANT]
> This fork supports Python 3.8+ only; earlier versions or Arduino libraries are not supported.

---

## 📦 Installation

> [!TIP]
> Use a virtual environment to avoid dependency conflicts and run:
>
> ```bash
> pip install dfrobot-environmental-sensor
> ```

## 🚀 Pythonic API usage

The library also exposes a modern, Pythonic API for direct use.
At the top level you’ll find:

`EnvironmentalSensor` → the main driver class

`Units` → supported measurement units (temperature & pressure)

`UVSensor` → supported UV sensor variants

### 🐍 Minimal example

> [!CAUTION]
> Ensure the I²C bus is enabled and the sensor’s address matches your hardware; some boards may use a different bus or address than `0x22`.

```python
from dfrobot_environmental_sensor import EnvironmentalSensor, Units, UVSensor

UV_VARIANT = UVSensor.LTR390UV  # or UVSensor.S12DS
# Create an I²C instance on bus 1
sensor = EnvironmentalSensor.i2c(bus=1, address=0x22, uv_sensor=UV_VARIANT)

if sensor.is_present():
    print("🌡️ Temperature:", sensor.read_temperature(Units.C), "°C")
    print("🌡️ Temperature:", sensor.read_temperature(Units.F), "°F")
    print("💧 Humidity:", sensor.read_humidity(), "%")
    print("☀️ UV Irradiance:", sensor.read_uv_irradiance(), "mW/cm²")
    print("💡 Light:", sensor.read_illuminance(), "lx")
    print("🌪️ Pressure:", sensor.read_pressure(Units.HPA), "hPa")
    print("🏔️ Altitude:", sensor.estimate_altitude(), "m")
else:
    print("❌ Sensor not detected.")
```

> [!NOTE]
> If the sensor isn’t detected, double-check wiring, power, and address configuration.

## 🛠️ Methods

```python
def is_present(self) -> bool:
    """Check if the sensor responds. Returns True if detected."""

def read_temperature(self, units: Units = Units.C) -> float:
    """Return ambient temperature in °C or °F."""

def read_humidity(self) -> float:
    """Return relative humidity (%)"""

def read_uv_irradiance(self) -> float:
    """Return UV irradiance (mW/cm²)."""

def read_illuminance(self) -> float:
    """Return ambient light level (lux)."""

def read_pressure(self, units: Units = Units.HPA) -> float:
    """Return atmospheric pressure in hPa or kPa."""

def estimate_altitude(self, sea_level_hpa: float = 1013.25) -> float:
    """Estimate altitude (m) from current pressure."""
```

## ✅ Compatibility

- Raspberry Pi (tested on Raspberry Pi 5)
- Python 3.8+ only

## 🔗 Product Links

|  |  |
|-------------------|-------------------|
| <img src="./images/SEN0500.png" alt="SEN0500" width="250"/> | <img src="./images/SEN0501.png" alt="SEN0501" width="250"/> |
| <p align="center">🌐 <a href="https://www.dfrobot.com/product-2522.html">SEN0500 – Fermion</a></p> | <p align="center">🌐 <a href="https://www.dfrobot.com/product-2528.html">SEN0501 – Gravity</a></p> |

## 📖 Changelog

The full changelog is available in [CHANGELOG.md](./CHANGELOG.md).

### Latest Release

> [!WARNING]
> Version 2.0.0 removes Arduino and Python 2.x support; projects relying on these should remain on earlier releases.

- **[2.0.0 – 2025-08-20]** 💥 Python-only fork
  - ✅ Python 3.8+ support with `smbus3`
  - ✅ Modernized README and examples
  - ❌ Dropped Arduino and Python 2.x support

### Previous Release (DFRobot upstream)

- **[1.1.0 – 2024-12-18]** ⚡️ Code updates from DFRobot
- **[1.0.0 – 2021-12-20]** ✨ Initial release by DFRobot (Arduino-compatible)

## 🙌 Credits

- Originally written by [tangjie133](https://github.com/tangjie133) (DFRobot), 2021
- Python 3.8+ fork maintained by [kallegrens](https://github.com/kallegrens), 2025
