import os
from os import path

from DeviceGateway import DeviceGateway
from time import sleep
from random import randrange as rand
from Emulators import TWANoiseEmulator, WGBTEmulator, NVIRVentilationemulator

if __name__ == "__main__":
    catalog_address = os.getenv("CATALOG_ADDRESS")
    if not catalog_address:
        raise ValueError("CATALOG_ADDRESS environment variable not set")
    
    cfg_file = os.getenv("CONFIG_FILE", "config.json")
    cfg_path = os.path.join(os.getcwd(), "configs", cfg_file)
    if not os.path.isfile(cfg_path):
        raise ValueError(f"Config file not found at path: {cfg_path}")
    
    gateway = DeviceGateway(catalog_address, cfg_path)
    gateway.Start()

    if os.getenv("EMULATOR"):
        try:
            freq = int(os.getenv("EMULATOR_FREQUENCY_SECONDS", "30"))
            type = os.getenv("EMULATOR_TYPE")
            if not type:
                raise ValueError("EMULATOR_TYPE environment variable not set")
            
            if type == "twa_noise":
                emulator = TWANoiseEmulator(gateway, freq)
            elif type == "wgbt":
                emulator = WGBTEmulator(gateway, freq)
            elif type == "nvir_ventilation":
                emulator = NVIRVentilationemulator(gateway, freq)
            else:
                raise ValueError(f"Unknown EMULATOR_TYPE: {type}")
            
            emulator.run()

        except Exception as e:
            print("Error while running emulator: ", e)
            gateway.Stop()

    else:
        while True:
            sleep(1)