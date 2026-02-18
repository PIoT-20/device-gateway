import requests as req
import os
import json
from MyMQTT import MyMQTT

class DeviceGateway:
    exposed = True

    def __init__(self, config_filename) -> None:
        self.catalog = os.getenv("CATALOG_ADDRESS")
        if not self.catalog:
            raise ValueError("CATALOG_ADDRESS environment variable not set")
        
        # Get device data and register the device if it doesn't have an id yet
        self.config = json.load(open(config_filename))
        if self.config.get("device_info", {}).get("device_id") is None:
            try:
                res = self.register()
                self.config["device_info"]["device_id"] = res["device_id"]
            except Exception as e:
                print("Error while registering: ", e)

        json.dump(self.config, open(config_filename, "w"))


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

    