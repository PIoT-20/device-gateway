import asyncio
import requests as req
import json
from MyMQTT import MyMQTT
from bleak import BleakScanner
import threading
from Device import Device

class CloudServices:
    exposed = True

    def __init__(self, catalog_address,  broker_host, broker_port) -> None:
        self.catalog = catalog_address
        if not self.catalog:
            raise ValueError("Catalog address must be specified")
        self.broker_host = broker_host
        self.broker_port = broker_port

        self.mqtt_client = MyMQTT("DeviceGatewayLocal", self.broker_host, self.broker_port, self)
    
    def register_device(self, device: Device):
        data = device.get_config()
        ret = req.post(f"{self.catalog}/device", json=data)
        if ret.status_code == 201:
            device.set_config(ret.json())
            print(f"Device {device.get_id()} registered successfully")
        else:
            raise Exception(ret.text)
        
    def Start(self):
        self.mqtt_client.start()

    def send_reading(self, id, reading):
        topic = f"devices/{id}/readings"
        self.mqtt_client.myPublish(topic, reading)
        print(f"Sent reading for device {id} to topic {topic}: {reading}")

    def Stop(self):
        self.mqtt_client.stop()
