

import json
from enum import Enum

# class syntax
class ConnectionStatus(Enum):
    CONNECTION_OFF = 1
    CONNECTION_ON = 2

class Device:
    def __init__(self, config=None, config_path=None):
        self._cfg_pth = config_path

        try: 
            if config:
                self._cfg = self.validate_config(config)
            elif self._cfg_pth:
                with open(self._cfg_pth, 'r') as f:
                    cfg = json.load(f)
                self._cfg = self.validate_config(cfg)
            else:
                raise ValueError("Either config or config_path must be provided")
        except ValueError as e:
            raise ValueError(f"Invalid initial configuration: {e}")
        
        self.connection_status = ConnectionStatus.CONNECTION_OFF
        
    def validate_config(self, cfg):
        if not cfg.get("client_id"):
            raise ValueError("Device info must contain a client_id")
        
        if not cfg.get("address"):
            raise ValueError("Device info must contain an address")

        if not cfg.get("connection", {}).get("protocol"):
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
            if(self._cfg_pth):
                with open(self._cfg_pth, 'w') as f:
                    json.dump(self._cfg, f)
        except ValueError as e:
            raise ValueError(f"Invalid configuration received: {e}")

    def get_config(self):
        return self._cfg

    def get_connection_info(self):
        return self._cfg.get("connection", {})
    
    def get_id(self):
        return self._cfg.get("device_id", None)
    
    def get_device_type(self):
        return self._cfg.get("device_type", None)
    

    
