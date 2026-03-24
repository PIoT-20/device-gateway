import requests as req
import os
import json
from MyMQTT import MyMQTT

class DeviceGateway:
    exposed = True

    def __init__(self, catalog_address, cfg_path) -> None:
        self.catalog = catalog_address
        if not self.catalog:
            raise ValueError("Catalog address must be specified")

        # Get device data and register the device if it doesn't have an id yet
        cfg_file = open(cfg_path, "r+")
        if not cfg_file:
            raise ValueError("Config file not found")
        self.config = json.load(cfg_file)
        cfg_file.close()

        if self.config.get("device_info", {}).get("device_id") is None:
            try:
                res = self.register()
                self.config["device_info"]["device_id"] = res["_id"]
            except Exception as e:
                print("Error while registering: ", e)

        json.dump(self.config, open(cfg_path, "w"))
        cfg_file.close()

        self.broker_host = os.getenv("BROKER_HOST")
        if not self.broker_host:
            raise ValueError("BROKER_HOST environment variable not set")
        
        self.broker_port = os.getenv("BROKER_PORT")
        if not self.broker_port:
            raise ValueError("BROKER_PORT environment variable not set")
        self.broker_port = int(self.broker_port)

        self.mqtt_client = MyMQTT("DeviceGatewayLocal", self.broker_host, self.broker_port, self)
    
    def register(self):
        data = self.config.get("device_info", {})
        if not data:
            raise ValueError("Device info is missing in config")

        ret = req.post(f"http://{self.catalog}/device", json=data)
        if ret.status_code == 200:
            return ret.json()
        else:
            raise Exception(f"Failed to register device: {ret.text}")

    def Start(self):
        self.mqtt_client.start()

    def send_reading(self, reading):
        device_id = self.config["device_info"]["device_id"]
        topic = f"devices/{device_id}/readings"
        self.mqtt_client.myPublish(topic, reading)

    def Stop(self):
        self.mqtt_client.stop()

    