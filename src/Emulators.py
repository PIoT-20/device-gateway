import asyncio
import datetime
import random
from random import randrange as rand
from Connections import Connection


# quality_level shifts the mean within the sensor range:
#   HIGH    = 25th percentile (closer to min / better conditions)
#   NORMAL = 50th percentile (midpoint)
#   LOW   = 75th percentile (closer to max / worse conditions)
QUALITY_MEAN_FACTOR = {"HIGH": 0.25, "NORMAL": 0.50, "LOW": 0.75}

# chaos_level controls the std deviation as a fraction of the range:
#   LOW    = tight cluster around the mean
#   NORMAL = moderate spread
#   HIGH   = wide spread, more outliers
CHAOS_STD_FACTOR = {"LOW": 0.05, "NORMAL": 0.12, "HIGH": 0.25}


class SensorEmulator(Connection):
    """Base class for sensor emulators supporting LIVE and DUMP modes."""
    
    def __init__(self, id, reading_cb, frequency_seconds=None, start_time=None, end_time=None, 
                 samples=None, quality_level="NORMAL", chaos_level="NORMAL"):
        """Initialize sensor emulator.
        
        LIVE mode: pass frequency_seconds
        DUMP mode: pass start_time, end_time, samples
        """
        super().__init__(id=id, reading_cb=reading_cb)
        
        self.frequency_seconds = frequency_seconds or 30        
        self.start_time = start_time
        self.end_time = end_time
        self.samples = samples
        self.quality_level = quality_level
        self.chaos_level = chaos_level

        # validation
        if start_time and end_time and (samples or frequency_seconds):
            self.is_dump_mode = True
        elif frequency_seconds and not (start_time or end_time or samples):
            self.is_dump_mode = False
        else:
            raise ValueError("Invalid configuration: For LIVE mode, provide frequency_seconds. For DUMP mode, provide start_time, end_time, and samples/frequency.")
        
        # Determine active mode

    async def run(self):
        if self.is_dump_mode:
            await self._run_dump_mode()
        else:
            await self._run_live_mode()

    async def _run_live_mode(self):
        """Generate readings in real-time."""
        while not self.is_stopped():
            reading = self._generate_reading()
            ts = datetime.datetime.now().isoformat()
            self.recv_reading(ts, reading)
            await asyncio.sleep(self.frequency_seconds)

    async def _run_dump_mode(self):
        """Replay pre-generated readings."""
        self.start_time = datetime.datetime.fromisoformat(self.start_time)
        self.end_time = datetime.datetime.fromisoformat(self.end_time)

        total_seconds = (self.end_time - self.start_time).total_seconds()
        if self.frequency_seconds:
            self.samples = int(total_seconds / self.frequency_seconds)
        else:
            self.frequency_seconds = total_seconds / self.samples
        
        current_time = self.start_time
        for i in range(self.samples):
            if self.is_stopped():
                break

            ts = current_time.isoformat()
            reading = self._generate_reading()
            self.recv_reading(ts, reading)

            current_time += datetime.timedelta(seconds=self.frequency_seconds)
            await asyncio.sleep(0.1)

    def _gauss(self, low, high):
        """Generate a gaussian sample clamped to [low, high], shaped by quality/chaos level."""
        span = high - low
        mean = low + span * QUALITY_MEAN_FACTOR.get(self.quality_level, 0.50)
        std = span * CHAOS_STD_FACTOR.get(self.chaos_level, 0.12)
        return max(low, min(high, round(random.gauss(mean, std))))

    # Methods to override in subclasses
    def _generate_reading(self):
        """Generate a single reading. Override in subclass."""
        raise NotImplementedError


class TWANoiseEmulator(SensorEmulator):
    LOWER_DB = 70
    UPPER_DB = 100
    
    def _generate_reading(self):
        return {"db": self._gauss(self.LOWER_DB, self.UPPER_DB)}

class WBGTEmulator(SensorEmulator):
    TNW_MIN = 18
    TNW_MAX = 30
    TG_MIN = 18
    TG_MAX = 34

    def _generate_reading(self):
        temp = self._gauss(self.TNW_MIN, self.TNW_MAX)
        return {
            "Tnw": temp,
            "Tg": self._gauss(self.TG_MIN, self.TG_MAX),
        }


class NVIRVentilationemulator(SensorEmulator):
    T_MIN = 15
    T_MAX = 30
    P_MIN = 800
    P_MAX = 1200
    CO2_MIN = 300
    CO2_MAX = 1200

    def _generate_reading(self):
        return {
            "T": self._gauss(self.T_MIN, self.T_MAX),
            "P": self._gauss(self.P_MIN, self.P_MAX),
            "CO2": self._gauss(self.CO2_MIN, self.CO2_MAX),
        }
