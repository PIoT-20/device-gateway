import os
from os import path

from DeviceGateway import DeviceGateway
from time import sleep
from random import randrange as rand
from Emulators import TWANoiseEmulator, WGBTEmulator, NVIRVentilationemulator
from CloudServices import CloudServices
from DeviceConfig import DeviceConfig

if __name__ == "__main__":
    catalog_address = os.getenv("CATALOG_ADDRESS")
    if not catalog_address:
        raise ValueError("CATALOG_ADDRESS environment variable not set")
    
    broker_host = os.getenv("BROKER_HOST")
    if not broker_host:
        raise ValueError("BROKER_HOST environment variable not set")
        
    broker_port = os.getenv("BROKER_PORT")
    if not broker_port:
        raise ValueError("BROKER_PORT environment variable not set")
    broker_port = int(broker_port)

    configs_dir = path.join(os.getcwd(), "configs")
    if not path.exists(configs_dir):
        raise ValueError(f"Configs directory not found at path: {configs_dir}")

    devices = [DeviceConfig(path.join(configs_dir, f)) for f in os.listdir(configs_dir) if f.endswith(".json")]
    cloud_service = CloudServices(catalog_address, broker_host, broker_port)
    gateway = DeviceGateway(cloud_service, devices)

    gateway.Start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        gateway.Stop()
