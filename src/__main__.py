import json
import os
from os import path
from random import randrange as rand
from time import sleep

from CloudServices import CloudServices
from Device import Device
from DeviceGateway import DeviceGateway

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

    config_path = path.join(os.getcwd(), "config.json")
    if not path.exists(config_path):
        raise ValueError(f"Config file not found at path: {config_path}")

    devices_ids = json.load(open(config_path, "r")).get("devices", [])
    if not devices_ids:
        raise ValueError("No devices found in config file")

    cloud_service = CloudServices(catalog_address, broker_host, broker_port)
    gateway = DeviceGateway(cloud_service, devices_ids)

    gateway.Start()

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        gateway.Stop()
