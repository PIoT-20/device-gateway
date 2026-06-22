from Connections import BLEAdvertisingConnection
from Emulators import TWANoiseEmulator, WBGTEmulator, NVIRVentilationemulator


class ConnectionFactory:
    @staticmethod
    def create_connection(device_id, connection_info, device_type, reading_cb):
        protocol = connection_info.get("protocol", None)
        if protocol == "BLE":
            return BLEAdvertisingConnection(device_id, reading_cb, connection_info.get("UUID", None), connection_info.get("MAJOR", None), connection_info.get("MINOR", None))
        if protocol == "EMULATOR":
            return EmulatorFactory.create_emulator(device_id, device_type, connection_info, reading_cb)
        else:
            raise ValueError(f"Unsupported connection protocol: {protocol}")


class EmulatorFactory:
    @staticmethod
    def create_emulator(device_id, device_type, connection_info, reading_cb):
        """Create emulator for given device type with LIVE or DUMP mode parameters."""
        emulator_type = connection_info.get("emulator_type", None)

        print(connection_info)
        
        # Extract parameters
        freq = connection_info.get("frequency_seconds")
        start_time = connection_info.get("start_time")
        end_time = connection_info.get("end_time")
        samples = connection_info.get("samples")
        quality_level = connection_info.get("quality_level", "NORMAL")
        chaos_level = connection_info.get("chaos_level", "NORMAL")
        
        # Validate based on mode
        if not (emulator_type == "LIVE" or emulator_type == "DUMP"):
            raise ValueError("Invalid emulator_type. Must be 'LIVE' or 'DUMP'.")

        # Map device type to emulator class
        emulator_classes = {
            "TWANoise": TWANoiseEmulator,
            "WBGT": WBGTEmulator,
            "NVIRVentilation": NVIRVentilationemulator,
        }
        
        emulator_class = emulator_classes.get(device_type)
        if not emulator_class:
            raise ValueError(f"Unsupported device type: {device_type}")
        
        return emulator_class(
            device_id, reading_cb,
            frequency_seconds=freq,
            start_time=start_time,
            end_time=end_time,
            samples=samples,
            quality_level=quality_level,
            chaos_level=chaos_level
        )
