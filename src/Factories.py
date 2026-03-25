from Connections import BLEAdvertisingConnection
from Emulators import TWANoiseEmulator, WBGTEmulator, NVIRVentilationemulator


class ConnectionFactory:
    @staticmethod
    def create_connection(device_id, connection_info, device_type, reading_cb):
        protocol = connection_info.get("protocol", None)
        if protocol == "BLE_ADVERTISING":
            return BLEAdvertisingConnection(device_id, reading_cb, connection_info.get("MAC", None))
        if protocol == "EMULATOR":
            return EmulatorFactory.create_emulator(device_type, connection_info, reading_cb)
        else:
            raise ValueError(f"Unsupported connection protocol: {protocol}")


class EmulatorFactory:
    @staticmethod
    def create_emulator(device_type, connection_info, reading_cb):
        freq = connection_info.get("frequency_seconds", 30)
        if device_type == "TWA-noise":
            return TWANoiseEmulator(id, reading_cb, freq)
        if device_type == "WBGT":
            return WBGTEmulator(id, reading_cb, freq)
        if device_type == "NVIR-ventilation":
            return NVIRVentilationemulator(id, reading_cb, freq)
        else:
            raise ValueError(f"Unsupported emulator type: {device_type}")
