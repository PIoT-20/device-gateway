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
            ret_data = ret.json()
            print(ret_data)
            ret_data["device_id"] = ret_data.pop("_id")["$oid"] # Rename _id to device_id
            
            if "device_id" not in ret_data:
                raise Exception("Invalid response from catalog: missing device_id")
            device.set_config(ret_data)
            
            if device.get_id() is None:
                raise Exception("Device ID not set after registration")
            
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
