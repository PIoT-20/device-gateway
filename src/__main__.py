import os
from os import path

from DeviceGateway import DeviceGateway
from time import sleep
from random import randrange as rand
from CloudServices import CloudServices
from Device import Device

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

    configs_dir = os.getenv("CONFIGS_DIR")
    if not configs_dir:
        configs_dir = path.join(os.getcwd(), "configs")

    if not path.exists(configs_dir):
        raise ValueError(f"Configs directory not found at path: {configs_dir}")

    devices = []
    for f in os.listdir(configs_dir):
        if f.endswith(".json"):
            try:
                device = Device(config_path=path.join(configs_dir, f))
                devices.append(device)
            except Exception as e:
                print(f"Error loading device from config {f}: {e}")

    cloud_service = CloudServices(catalog_address, broker_host, broker_port)
    gateway = DeviceGateway(cloud_service, devices)

    gateway.Start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        gateway.Stop()
