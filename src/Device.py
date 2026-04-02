

import json
from enum import Enum

# class syntax
class ConnectionStatus(Enum):
    CONNECTION_OFF = 1
    CONNECTION_ON = 2

class Device:
    def __init__(self, config_path, config=None):
        if not config_path:
            raise ValueError("Config path must be provided")

        self._cfg_pth = config_path

        try: 
            if config:
                self.set_config(config)
            elif self._cfg_pth:
                with open(self._cfg_pth, 'r') as f:
                    cfg = json.load(f)
                self.set_config(cfg)

        except ValueError as e:
            raise ValueError(f"Invalid initial configuration: {e}")
        
        except FileNotFoundError as e:
            raise ValueError(f"Configuration file not found: {e}")
        
        except Exception as e:
            raise Exception(f"Error loading initial configuration: {e}")
        
        self.connection_status = ConnectionStatus.CONNECTION_OFF

        print(f"Device initialized. Cfg file: {self._cfg_pth}\n")
        
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
            if(self._cfg_pth):
                with open(self._cfg_pth, 'w') as f:
                    json.dump(self._cfg, f)
        except ValueError as e:
            raise ValueError(f"Invalid configuration received: {e}")
        except Exception as e:
            raise Exception(f"Error saving configuration: {e}")

    def get_config(self):
        return self._cfg
    
    def get_cfg_file(self):
        return self._cfg_pth

    def get_connection_info(self):
        return self._cfg.get("connection_info", {})
    
    def get_id(self):
        return self._cfg.get("device_id", None)
    
    def get_device_type(self):
        return self._cfg.get("device_type", None)
    

    
