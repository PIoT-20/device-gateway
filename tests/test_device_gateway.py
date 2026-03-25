import sys
import os
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from DeviceGateway import DeviceGateway
from Device import ConnectionStatus


def _make_mock_device(device_id="dev-001", has_id=True, connection_status=ConnectionStatus.CONNECTION_OFF):
    device = MagicMock()
    device.get_id.return_value = device_id if has_id else None
    device.get_connection_info.return_value = {"protocol": "EMULATOR"}
    device.get_device_type.return_value = "TWA-noise"
    device.get_connection_status.return_value = connection_status
    return device


def _make_mock_cloud():
    cloud = MagicMock()
    return cloud


class TestDeviceGatewayInit(unittest.TestCase):
    def test_stores_cloud_service_and_devices(self):
        cloud = _make_mock_cloud()
        devices = [_make_mock_device("d1"), _make_mock_device("d2")]

        gw = DeviceGateway(cloud, devices)

        self.assertIs(gw.cloud_service, cloud)
        self.assertEqual(len(gw.devices), 2)


class TestHandleReading(unittest.TestCase):
    def test_forwards_reading_to_cloud(self):
        cloud = _make_mock_cloud()
        gw = DeviceGateway(cloud, [])

        reading = {"db": 85}
        gw.handle_reading("dev-001", reading)

        cloud.send_reading.assert_called_once_with("dev-001", reading)


class TestDeviceGatewayStart(unittest.TestCase):
    @patch("DeviceGateway.ConnectionFactory")
    def test_connects_all_devices(self, mock_factory):
        mock_conn = MagicMock()
        mock_factory.create_connection.return_value = mock_conn
        cloud = _make_mock_cloud()
        d1 = _make_mock_device("d1")
        d2 = _make_mock_device("d2")
        gw = DeviceGateway(cloud, [d1, d2])

        gw.Start()

        d1.connect.assert_called_once_with(mock_conn)
        d2.connect.assert_called_once_with(mock_conn)

    def test_registers_device_without_id(self):
        cloud = _make_mock_cloud()
        device = _make_mock_device(has_id=False)
        gw = DeviceGateway(cloud, [device])

        with patch("DeviceGateway.ConnectionFactory"):
            gw.Start()

        cloud.register_device.assert_called_once_with(device)

    def test_does_not_register_device_with_id(self):
        cloud = _make_mock_cloud()
        device = _make_mock_device("d1")
        gw = DeviceGateway(cloud, [device])

        with patch("DeviceGateway.ConnectionFactory"):
            gw.Start()

        cloud.register_device.assert_not_called()

    def test_removes_device_on_registration_error(self):
        cloud = _make_mock_cloud()
        cloud.register_device.side_effect = Exception("registration failed")
        bad_device = _make_mock_device(has_id=False)
        good_device = _make_mock_device("d2")
        gw = DeviceGateway(cloud, [bad_device, good_device])

        with patch("DeviceGateway.ConnectionFactory"):
            gw.Start()

        self.assertNotIn(bad_device, gw.devices)
        good_device.connect.assert_called_once()


class TestDeviceGatewayStop(unittest.TestCase):
    def test_disconnects_connected_devices(self):
        cloud = _make_mock_cloud()
        d1 = _make_mock_device("d1", connection_status=ConnectionStatus.CONNECTION_ON)
        d2 = _make_mock_device("d2", connection_status=ConnectionStatus.CONNECTION_OFF)
        gw = DeviceGateway(cloud, [d1, d2])

        gw.Stop()

        d1.disconnect.assert_called_once()
        d2.disconnect.assert_not_called()

    def test_stops_cloud_service(self):
        cloud = _make_mock_cloud()
        gw = DeviceGateway(cloud, [])

        gw.Stop()

        cloud.Stop.assert_called_once()

    def test_stop_with_no_devices(self):
        cloud = _make_mock_cloud()
        gw = DeviceGateway(cloud, [])

        gw.Stop()

        cloud.Stop.assert_called_once()


if __name__ == "__main__":
    unittest.main()
