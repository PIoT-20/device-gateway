# device-gateway

The device gateway is the bridge between physical (or emulated) sensors and the PIoT-20 cloud services. It loads each device's configuration from the catalog, opens a connection to the device, and publishes every reading to the MQTT broker.

## How it works

1. Reads the device IDs listed in `config.json`.
2. Fetches each device's configuration from the catalog (`GET /device?device_id=<id>`). Devices whose configuration fails to load or validate are skipped.
3. Uses `ConnectionFactory` to create a connection based on `connection_info.protocol`. Each connection runs in its own thread.
4. Publishes each reading to `devices/<device_id>/readings`:

```json
{ "timestamp": "2026-01-15T10:30:00", "data": { "db": 82 } }
```

## Configuration

`config.json` lists the devices this gateway handles:

```json
{ "devices": ["<catalog device id>", "..."] }
```

| Env var | Description |
|---|---|
| `CATALOG_ADDRESS` | Catalog base URL, e.g. `http://catalog:8080` |
| `BROKER_HOST` | MQTT broker host |
| `BROKER_PORT` | MQTT broker port |

## Connection protocols

The protocol is set in the device's `connection_info` in the catalog.

### `EMULATOR`

Generates synthetic readings for the device's `device_type`:

| `device_type` | Fields | Range |
|---|---|---|
| `TWANoise` | `db` | 70–100 |
| `WBGT` | `Tnw`, `Tg` | 18–30, 18–34 °C |
| `NVIRVentilation` | `T`, `P`, `CO2` | 15–30 °C, 800–1200 hPa, 300–1200 ppm |

Values are drawn from a Gaussian distribution, clamped to the range:

- `quality_level` sets where the mean sits in the range: `HIGH` = 25th percentile (better conditions), `NORMAL` = midpoint, `LOW` = 75th percentile (worse conditions).
- `chaos_level` sets the spread: `LOW`, `NORMAL` or `HIGH`.

Emulators run in one of two modes, set by `emulator_type`:

**LIVE** emits one reading every `frequency_seconds`, timestamped with the current time.

```json
{ "protocol": "EMULATOR", "emulator_type": "LIVE", "frequency_seconds": 30,
  "quality_level": "NORMAL", "chaos_level": "LOW" }
```

**DUMP** quickly replays a historical window (one reading every 0.1 s of real time). Use it to backfill data for testing the quality index. Give `start_time` and `end_time`, plus either `samples` or `frequency_seconds`.

```json
{ "protocol": "EMULATOR", "emulator_type": "DUMP",
  "start_time": "2026-01-05T08:00:00", "end_time": "2026-01-09T19:00:00",
  "frequency_seconds": 300, "quality_level": "LOW", "chaos_level": "NORMAL" }
```

### `BLE`

Scans for BLE advertisements (`UUID`, `MAJOR`, `MINOR` fields) using [bleak](https://github.com/hbldh/bleak). Filtering and decoding advertisements is **not implemented yet**, so BLE devices don't publish any readings.

BLE needs access to the host's Bluetooth stack. In Docker this means running privileged with `/run/dbus` and `/dev/bus/usb` mounted, as the devops compose file does. This only works on a Linux host.

## Running

```sh
pip install -r requirements.txt
CATALOG_ADDRESS=http://localhost:8085 BROKER_HOST=localhost BROKER_PORT=1883 python src/__main__.py
```

Run it from the repo root, so that `config.json` is found in the working directory. In the full stack, start it with `docker compose up device-gateway` from the [devops](https://github.com/PIoT-20/devops) repo.

## Tests

```sh
python -m pytest tests
python -m pytest tests/test_emulators.py
```

## Project structure

```
src/
  DeviceGateway.py   loads devices and wires up their connections
  CloudServices.py   catalog REST client and MQTT publisher
  Device.py          device config validation and connection state
  Factories.py       ConnectionFactory / EmulatorFactory
  Connections.py     threaded Connection base class and BLE connection
  Emulators.py       sensor emulators (LIVE/DUMP)
  MyMQTT.py          paho-mqtt wrapper
```

To add a new sensor type, add a `SensorEmulator` subclass that implements `_generate_reading()`, then map it to its `device_type` in `EmulatorFactory`.
