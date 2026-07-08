
import asyncio
from datetime import datetime
import threading

from bleak import BleakScanner


class Connection:
    def __init__(self, id, reading_cb):
        self.id = id
        self.reading_cb = reading_cb
        self._stop_event = threading.Event()
        self._thread = None

    def recv_reading(self, ts, data):
        reading = {
            "timestamp": ts,
            "data": data
        }
        self.reading_cb(self.id, reading)

    def Start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_async, daemon=True)
        self._thread.start()

    def _run_async(self):
        asyncio.run(self.run())

    def Stop(self):
        self._stop_event.set()

    def join(self):
        if self._thread:
            self._thread.join()

    def is_stopped(self):
        return self._stop_event.is_set()

    async def run(self):
        pass

class BLEAdvertisingConnection(Connection):
    def __init__(self, id, reading_cb, uuid, major, minor):
        super().__init__(id, reading_cb)
        self.uuid = uuid
        self.major = major
        self.minor = minor

    def detection_cb(self, device, advertisement_data):
        # TODO: filter by uuid, major and minor
        return
        ts = datetime.now().isoformat()
        self.recv_reading(ts, advertisement_data)

    async def run(self):
        while not self.is_stopped():
            await BleakScanner.discover(timeout=5.0, detection_callback=self.detection_cb)


