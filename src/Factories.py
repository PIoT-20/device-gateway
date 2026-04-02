from Connections import BLEAdvertisingConnection
from Emulators import TWANoiseEmulator, WBGTEmulator, NVIRVentilationemulator


class ConnectionFactory:
    @staticmethod
    def create_connection(device_id, connection_info, device_type, reading_cb):
        protocol = connection_info.get("protocol", None)
        if protocol == "BLE_ADVERTISING":
            return BLEAdvertisingConnection(device_id, reading_cb, connection_info.get("MAC", None))
        if protocol == "EMULATOR":
            return EmulatorFactory.create_emulator(device_id, device_type, connection_info, reading_cb)
        else:
            raise ValueError(f"Unsupported connection protocol: {protocol}")


class EmulatorFactory:
    @staticmethod
    def create_emulator(device_id, device_type, connection_info, reading_cb):
        """Create emulator for given device type with LIVE or DUMP mode parameters."""
        emulator_type = connection_info.get("emulator_type", None)
        
        # Extract parameters
        freq = connection_info.get("frequency_seconds")
        start_time = connection_info.get("start_time")
        end_time = connection_info.get("end_time")
        samples = connection_info.get("samples")
        quality_level = connection_info.get("quality_level", "NORMAL")
        chaos_level = connection_info.get("chaos_level", "NORMAL")
        
        # Validate based on mode
        if emulator_type == "LIVE" and not freq:
            raise ValueError("LIVE emulator requires frequency_seconds")
        elif emulator_type == "DUMP" and not (start_time and end_time and samples):
            raise ValueError("DUMP emulator requires start_time, end_time, and samples")
        elif not emulator_type:
            raise ValueError("emulator_type must be specified")
        
        # Map device type to emulator class
        emulator_classes = {
            "TWA-noise": TWANoiseEmulator,
            "WBGT": WBGTEmulator,
            "NVIR-ventilation": NVIRVentilationemulator,
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
