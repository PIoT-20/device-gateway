import asyncio

from random import randrange as rand
from Connections import Connection


class DeviceEmulator(Connection):
    def __init__(self, id, reading_cb, frequency_seconds=30):
        super().__init__(id=id, reading_cb=reading_cb)
        self.frequency_seconds = frequency_seconds

    async def run(self):
        while not self.is_stopped():
            reading = self._generate_reading()
            print("Sending reading: ", reading)
            self.recv_reading(reading)
            await asyncio.sleep(self.frequency_seconds)

    def _generate_reading(self):
        pass  # To be implemented by subclasses


class TWANoiseEmulator(DeviceEmulator):
    def _generate_reading(self):
        return {
            "db": rand(70, 100)
        }

class WBGTEmulator(DeviceEmulator):
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