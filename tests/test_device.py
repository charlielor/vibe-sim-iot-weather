"""
Tests for the IoT device simulator
"""

import unittest
from src.vibe_sim_iot_simulator.core.device import IoTDevice


class TestIoTDevice(unittest.TestCase):
    def test_device_initialization(self):
        device = IoTDevice("test-device", ["temperature", "humidity"])
        self.assertEqual(device.device_id, "test-device")
        self.assertEqual(device.sensor_types, ["temperature", "humidity"])

    def test_generate_reading(self):
        device = IoTDevice("test-device", ["temperature"])
        reading = device.generate_reading("temperature")
        self.assertIn("value", reading)
        self.assertIn("unit", reading)
        self.assertEqual(reading["unit"], "°C")
        self.assertTrue(15 <= reading["value"] <= 30)


if __name__ == "__main__":
    unittest.main()
