import sys
import os
import json
import unittest
import tempfile
import shutil
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from Device import Device, ConnectionStatus


VALID_CONFIG = {
    "device_id": "dev-001",
    "user_id": "client-001",
    "address": "192.168.1.10",
    "device_type": "TWA-noise",
    "connection": {
        "protocol": "EMULATOR",
        "frequency_seconds": 5,
    },
}

# Temporary directory for test config files
TEMP_DIR = tempfile.mkdtemp()

def get_temp_config_path(filename="test_device_config.json"):
    """Get path for temporary config file."""
    return os.path.join(TEMP_DIR, filename)

TMP_CFG_PATH = get_temp_config_path()

def _make_config(**overrides):
    cfg = {**VALID_CONFIG, **overrides}
    return cfg


class TestDeviceInit(unittest.TestCase):
    def test_init_with_valid_config(self):
        device = Device(TMP_CFG_PATH, config=VALID_CONFIG)
        self.assertEqual(device.get_id(), "dev-001")
        self.assertEqual(device.get_device_type(), "TWA-noise")
        self.assertEqual(device.get_connection_status(), ConnectionStatus.CONNECTION_OFF)
        os.remove(TMP_CFG_PATH)

    def test_init_with_config_path(self, ):
        with open(TMP_CFG_PATH, "w") as f:
            json.dump(VALID_CONFIG, f)
        try:
            device = Device(TMP_CFG_PATH)
            self.assertEqual(device.get_id(), "dev-001")
        finally:
            os.remove(TMP_CFG_PATH)

    def test_init_no_config_raises(self):
        with self.assertRaises(ValueError):
            Device(get_temp_config_path("nonexistent.json"))

    def test_missing_user_id_raises(self):
        cfg = _make_config(user_id=None)
        with self.assertRaises(ValueError):
            Device(TMP_CFG_PATH, config=cfg)

    def test_missing_address_raises(self):
        cfg = _make_config(address=None)
        with self.assertRaises(ValueError):
            Device(TMP_CFG_PATH, config=cfg)

    def test_missing_protocol_raises(self):
        cfg = _make_config(connection={"frequency_seconds": 5})
        with self.assertRaises(ValueError):
            Device(TMP_CFG_PATH, config=cfg)


class TestDeviceGetters(unittest.TestCase):
    def setUp(self):
        self.device = Device(TMP_CFG_PATH, config=VALID_CONFIG)

    def test_get_config_returns_full_config(self):
        cfg = self.device.get_config()
        self.assertEqual(cfg["user_id"], "client-001")
        self.assertEqual(cfg["address"], "192.168.1.10")

    def test_get_connection_info(self):
        info = self.device.get_connection_info()
        self.assertEqual(info["protocol"], "EMULATOR")

    def test_get_device_type(self):
        self.assertEqual(self.device.get_device_type(), "TWA-noise")

    def test_get_id(self):
        self.assertEqual(self.device.get_id(), "dev-001")


class TestDeviceConnection(unittest.TestCase):
    def setUp(self):
        self.device = Device(TMP_CFG_PATH, config=VALID_CONFIG)
        self.mock_connection = MagicMock()

    def test_connect_starts_connection(self):
        self.device.connect(self.mock_connection)

        self.mock_connection.Start.assert_called_once()
        self.assertEqual(self.device.get_connection_status(), ConnectionStatus.CONNECTION_ON)

    def test_disconnect_stops_connection(self):
        self.device.connect(self.mock_connection)

        self.device.disconnect()

        self.mock_connection.Stop.assert_called_once()
        self.mock_connection.join.assert_called_once()
        self.assertEqual(self.device.get_connection_status(), ConnectionStatus.CONNECTION_OFF)


class TestDeviceSetConfig(unittest.TestCase):
    def test_set_config_valid(self):
        with open(TMP_CFG_PATH, "w") as f:
            json.dump(VALID_CONFIG, f)
        try:
            device = Device(config_path=TMP_CFG_PATH)
            new_cfg = _make_config(address="10.0.0.1")
            device.set_config(new_cfg)

            self.assertEqual(device.get_config()["address"], "10.0.0.1")

            with open(TMP_CFG_PATH, "r") as f:
                saved = json.load(f)
            self.assertEqual(saved["address"], "10.0.0.1")
        finally:
            os.remove(TMP_CFG_PATH)

    def test_set_config_invalid_raises(self):
        device = Device(TMP_CFG_PATH, config=VALID_CONFIG)
        bad_cfg = _make_config(user_id=None)
        with self.assertRaises(ValueError):
            device.set_config(bad_cfg)


if __name__ == "__main__":
    try:
        unittest.main()
    finally:
        # Clean up temporary directory
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
