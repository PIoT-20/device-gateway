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

    def __init__(self, cloud_service: CloudServices, devices_ids: list[str]) -> None:
        self.cloud_service = cloud_service
        self.devices_ids = devices_ids
        self.devices = []

    def handle_reading(self, device_id, reading):
        self.cloud_service.send_reading(device_id, reading)

    def Start(self):
        self.cloud_service.Start()

        failed_devices = []
        for device_id in self.devices_ids:
            try:
                config = self.cloud_service.get_device_config(device_id)
                device = Device(config)
                self.devices.append(device)
            except Exception as e:
                print(f"Error getting device config for {device_id}: {e}")
                failed_devices.append(device_id)

        # Remove failed devices
        for device_id in failed_devices:
            self.devices_ids.remove(device_id)

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