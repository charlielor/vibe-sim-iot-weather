"""
Run a multi-device IoT simulation
"""

import random
import threading
from core.device import IoTDevice


def device_simulation_thread(device_id, sensors, interval, duration, db_path):
    """Function to run in a separate thread for each device"""
    device = IoTDevice(device_id=device_id, sensor_types=sensors)
    # Each device gets its own connection to the database
    device.connect_to_db(db_path=db_path)
    device.run_simulation(interval=interval, duration=duration)


def run_multi_device_simulation(num_devices=3, duration=60, db_path="iot_data.duckdb"):
    """Run a simulation with multiple IoT devices concurrently using threads"""

    # Define possible sensor combinations
    sensor_combinations = [
        ["temperature", "humidity"],
        ["temperature", "humidity", "light"],
        ["temperature", "pressure"],
        ["light", "motion"],
        ["temperature", "humidity", "pressure", "light"],
    ]

    # Create and start threads for each device
    threads = []
    for i in range(num_devices):
        device_id = f"device-{i + 1:02d}"
        # Randomly select a sensor combination
        sensors = random.choice(sensor_combinations)
        # Use different intervals for each device
        interval = random.randint(2, 10)

        # Create and start a thread for this device
        thread = threading.Thread(
            target=device_simulation_thread,
            args=(device_id, sensors, interval, duration, db_path),
        )
        thread.start()
        threads.append(thread)
        print(f"Started simulation thread for {device_id}")

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print("All device simulations completed")


def main():
    run_multi_device_simulation(num_devices=5, duration=120)


if __name__ == "__main__":
    main()
