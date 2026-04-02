import asyncio
import requests as req
import json
from MyMQTT import MyMQTT
from bleak import BleakScanner
import threading
from Device import Device, ConnectionStatus
from Factories import ConnectionFactory
from CloudServices import CloudServices

class DeviceGateway:
    exposed = True

    def __init__(self, cloud_service: CloudServices, devices: list[Device]) -> None:
        self.cloud_service = cloud_service
        self.devices = devices
            
    
    def handle_reading(self, device_id, reading):
        self.cloud_service.send_reading(device_id, reading)

    def Start(self):
        self.cloud_service.Start()

        failed_devices = []
        for device in self.devices:
            if not device.get_id():
                try:
                    self.cloud_service.register_device(device)
                except Exception as e:
                    print(f"Error registering device {device.get_cfg_file()}: {e}")
                    failed_devices.append(device)
        
        # Remove failed devices
        for device in failed_devices:
            self.devices.remove(device)

        for device in self.devices:
            try:
                connection = ConnectionFactory.create_connection(
                    device.get_id(),
                    device.get_connection_info(),
                    device.get_device_type(),
                    self.handle_reading,
                )
                device.connect(connection)
            except ValueError as e:
                print(f"Error creating connection for device {device.get_id()}: {e}")

    def Stop(self):
        for device in self.devices:
            if device.get_connection_status() == ConnectionStatus.CONNECTION_ON:
                device.disconnect()
        self.cloud_service.Stop()