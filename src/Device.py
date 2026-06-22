

import json
from enum import Enum

# class syntax
class ConnectionStatus(Enum):
    CONNECTION_OFF = 1
    CONNECTION_ON = 2

class Device:
    def __init__(self, config=None):
        if not config:
            raise ValueError("Config must be provided")
        
        self.set_config(config)
        self.connection_status = ConnectionStatus.CONNECTION_OFF

        print(f"Device {self.get_id()} initialized.")
        
    def validate_config(self, cfg):
        if not cfg.get("device_type"):
            raise ValueError("Device info must contain a device_type")

        if not cfg.get("user_id"):
            raise ValueError("Device info must contain a user_id")
        
        if not cfg.get("location"):
            raise ValueError("Device info must contain an location")

        if not cfg.get("connection_info", {}).get("protocol"):
            raise ValueError("Connection info must contain a protocol")
        
        return cfg
    
    def connect(self, connection):
        self.connection = connection
        self.connection.Start()
        self.connection_status = ConnectionStatus.CONNECTION_ON

    def disconnect(self):
        if self.connection:
            self.connection.Stop()
            self.connection.join()
            self.connection_status = ConnectionStatus.CONNECTION_OFF

    def get_connection_status(self):
        return self.connection_status

    def set_config(self, cfg):
        try:
            self._cfg = self.validate_config(cfg)
        except ValueError as e:
            raise ValueError(f"Invalid configuration received: {e}")
        except Exception as e:
            raise Exception(f"Error saving configuration: {e}")

    def get_config(self):
        return self._cfg

    def get_connection_info(self):
        return self._cfg.get("connection_info", {})
    
    def get_id(self):
        return self._cfg.get("_id", {}).get("$oid")
    
    def get_device_type(self):
        return self._cfg.get("device_type", None)
    

    
