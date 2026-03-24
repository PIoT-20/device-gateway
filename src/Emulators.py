from DeviceGateway import DeviceGateway
from time import sleep
from random import randrange as rand


class DeviceEmulator:
    def __init__(self, gateway: DeviceGateway, frequency_seconds=30):
        self.gateway = gateway
        self.frequency_seconds = frequency_seconds

    def run(self):
        while True:
            reading = self._generate_reading()
            print("Sending reading: ", reading)
            self.gateway.send_reading(reading)
            sleep(self.frequency_seconds)

    def _generate_reading(self):
        pass  # To be implemented by subclasses


class TWANoiseEmulator(DeviceEmulator):
    def _generate_reading(self):
        return {
            "db": rand(70, 100)
        }

class WGBTEmulator(DeviceEmulator):
    def _generate_reading(self):
        temp = rand(18, 30)  # Warmer during work hours
        return {
            "Tnw": temp,
            "Tg": temp + rand(0, 4),  # Add some variability
        }        

class NVIRVentilationemulator(DeviceEmulator):
    def _generate_reading(self):
        return {
            "T": rand(15, 30),
            "P": rand(800, 1200),
            "CO2": rand(300, 1200),
        }