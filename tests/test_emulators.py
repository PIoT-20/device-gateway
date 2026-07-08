import sys
import os
import unittest
from unittest.mock import MagicMock
import statistics

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from Emulators import TWANoiseEmulator, WBGTEmulator, NVIRVentilationemulator

SAMPLES = 200


def _make(cls, quality="NORMAL", chaos="NORMAL"):
    emu = cls(id="test", reading_cb=MagicMock())
    emu.samples = SAMPLES
    emu.quality_level = quality
    emu.chaos_level = chaos
    return emu


class TestLiveReadingKeys(unittest.TestCase):
    def test_twa_noise(self):
        emu = TWANoiseEmulator(id="t", reading_cb=MagicMock())
        self.assertIn("db", emu._generate_reading())

    def test_wbgt(self):
        emu = WBGTEmulator(id="t", reading_cb=MagicMock())
        r = emu._generate_reading()
        self.assertIn("Tnw", r)
        self.assertIn("Tg", r)

    def test_nvir(self):
        emu = NVIRVentilationemulator(id="t", reading_cb=MagicMock())
        r = emu._generate_reading()
        for key in ("T", "P", "CO2"):
            self.assertIn(key, r)


class TestQualityShiftsMean(unittest.TestCase):
    def _assert_mean_shifts(self, cls, key):
        low = statistics.mean(r[key] for r in _make(cls, quality="LOW")._generate_all_readings())
        high = statistics.mean(r[key] for r in _make(cls, quality="HIGH")._generate_all_readings())
        self.assertGreater(high, low)

    def test_twa_noise(self):
        self._assert_mean_shifts(TWANoiseEmulator, "db")

    def test_wbgt(self):
        self._assert_mean_shifts(WBGTEmulator, "Tnw")

    def test_nvir(self):
        self._assert_mean_shifts(NVIRVentilationemulator, "CO2")


class TestChaosChangesSpread(unittest.TestCase):
    def _assert_spread_increases(self, cls, key):
        low = statistics.stdev(r[key] for r in _make(cls, chaos="LOW")._generate_all_readings())
        high = statistics.stdev(r[key] for r in _make(cls, chaos="HIGH")._generate_all_readings())
        self.assertGreater(high, low)

    def test_twa_noise(self):
        self._assert_spread_increases(TWANoiseEmulator, "db")

    def test_wbgt(self):
        self._assert_spread_increases(WBGTEmulator, "Tnw")

    def test_nvir(self):
        self._assert_spread_increases(NVIRVentilationemulator, "CO2")


if __name__ == "__main__":
    unittest.main()
