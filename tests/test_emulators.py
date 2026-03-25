import sys
import os
import asyncio
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from Emulators import (
    TWANoiseEmulator,
    WBGTEmulator,
    NVIRVentilationemulator,
)
from Factories import EmulatorFactory


class TestTWANoiseEmulator(unittest.TestCase):
    def setUp(self):
        self.cb = MagicMock()
        self.emulator = TWANoiseEmulator(id="noise-1", reading_cb=self.cb)

    def test_reading_has_db_key(self):
        reading = self.emulator._generate_reading()
        self.assertIn("db", reading)

    def test_db_value_in_range(self):
        for _ in range(50):
            reading = self.emulator._generate_reading()
            self.assertGreaterEqual(reading["db"], 70)
            self.assertLess(reading["db"], 100)


class TestWBGTEmulator(unittest.TestCase):
    def setUp(self):
        self.cb = MagicMock()
        self.emulator = WBGTEmulator(id="wbgt-1", reading_cb=self.cb)

    def test_reading_has_expected_keys(self):
        reading = self.emulator._generate_reading()
        self.assertIn("Tnw", reading)
        self.assertIn("Tg", reading)

    def test_tnw_in_range(self):
        for _ in range(50):
            reading = self.emulator._generate_reading()
            self.assertGreaterEqual(reading["Tnw"], 18)
            self.assertLess(reading["Tnw"], 30)

    def test_tg_greater_or_equal_to_tnw(self):
        for _ in range(50):
            reading = self.emulator._generate_reading()
            self.assertGreaterEqual(reading["Tg"], reading["Tnw"])


class TestNVIRVentilationEmulator(unittest.TestCase):
    def setUp(self):
        self.cb = MagicMock()
        self.emulator = NVIRVentilationemulator(id="nvir-1", reading_cb=self.cb)

    def test_reading_has_expected_keys(self):
        reading = self.emulator._generate_reading()
        self.assertIn("T", reading)
        self.assertIn("P", reading)
        self.assertIn("CO2", reading)

    def test_temperature_in_range(self):
        for _ in range(50):
            reading = self.emulator._generate_reading()
            self.assertGreaterEqual(reading["T"], 15)
            self.assertLess(reading["T"], 30)

    def test_pressure_in_range(self):
        for _ in range(50):
            reading = self.emulator._generate_reading()
            self.assertGreaterEqual(reading["P"], 800)
            self.assertLess(reading["P"], 1200)

    def test_co2_in_range(self):
        for _ in range(50):
            reading = self.emulator._generate_reading()
            self.assertGreaterEqual(reading["CO2"], 300)
            self.assertLess(reading["CO2"], 1200)


class TestEmulatorRun(unittest.TestCase):
    def test_run_calls_callback(self):
        cb = MagicMock()
        emulator = TWANoiseEmulator(id="run-test", reading_cb=cb, frequency_seconds=0)

        async def run_briefly():
            task = asyncio.create_task(emulator.run())
            await asyncio.sleep(0.05)
            emulator.Stop()
            await task

        asyncio.run(run_briefly())
        self.assertGreater(cb.call_count, 0)

    def test_run_passes_id_and_reading(self):
        cb = MagicMock()
        emulator = TWANoiseEmulator(id="id-test", reading_cb=cb, frequency_seconds=0)

        async def run_briefly():
            task = asyncio.create_task(emulator.run())
            await asyncio.sleep(0.05)
            emulator.Stop()
            await task

        asyncio.run(run_briefly())
        call_args = cb.call_args
        self.assertEqual(call_args[0][0], "id-test")
        self.assertIn("db", call_args[0][1])


class TestEmulatorFactory(unittest.TestCase):
    def _conn_info(self, frequency=10):
        return {"frequency_seconds": frequency}

    def test_create_twa_noise(self):
        emulator = EmulatorFactory.create_emulator("TWA-noise", self._conn_info(), MagicMock())
        self.assertIsInstance(emulator, TWANoiseEmulator)

    def test_create_wbgt(self):
        emulator = EmulatorFactory.create_emulator("WBGT", self._conn_info(), MagicMock())
        self.assertIsInstance(emulator, WBGTEmulator)

    def test_create_nvir_ventilation(self):
        emulator = EmulatorFactory.create_emulator("NVIR-ventilation", self._conn_info(), MagicMock())
        self.assertIsInstance(emulator, NVIRVentilationemulator)

    def test_unsupported_type_raises(self):
        with self.assertRaises(ValueError):
            EmulatorFactory.create_emulator("unknown-type", self._conn_info(), MagicMock())


if __name__ == "__main__":
    unittest.main()
