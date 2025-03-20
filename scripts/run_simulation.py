"""
Run a single IoT device simulation
"""

from core.device import IoTDevice


def main():
    # Create a simulated IoT device with multiple sensors
    device = IoTDevice(
        device_id="kitchen-sensor-01", sensor_types=["temperature", "humidity", "light"]
    )

    # Run the simulation for 30 seconds, taking readings every 3 seconds
    device.run_simulation(interval=3, duration=30)


if __name__ == "__main__":
    main()
