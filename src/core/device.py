import time
import random
import duckdb
import datetime
import os


class IoTDevice:
    def __init__(self, device_id, sensor_types):
        """
        Initialize an IoT device simulator

        Args:
            device_id (str): Unique identifier for the device
            sensor_types (list): List of sensors this device has
        """
        self.device_id = device_id
        self.sensor_types = sensor_types
        self.db_conn = None

    def connect_to_db(self, db_path="iot_data.duckdb"):
        """Connect to the DuckDB database"""
        # Create the database directory if it doesn't exist
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        # Connect to the database
        self.db_conn = duckdb.connect(db_path)

        # Create the table if it doesn't exist
        self.db_conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                timestamp TIMESTAMP,
                device_id VARCHAR,
                sensor_type VARCHAR,
                value DOUBLE,
                unit VARCHAR
            )
        """)

        print(f"Connected to database: {db_path}")

    def generate_reading(self, sensor_type):
        """Generate a simulated sensor reading"""
        if sensor_type == "temperature":
            # Simulate temperature between 15-30°C with some random variation
            return {"value": round(random.uniform(15, 30), 2), "unit": "°C"}
        elif sensor_type == "humidity":
            # Simulate humidity between 30-80%
            return {"value": round(random.uniform(30, 80), 2), "unit": "%"}
        elif sensor_type == "pressure":
            # Simulate atmospheric pressure around 1000 hPa
            return {"value": round(random.uniform(980, 1020), 2), "unit": "hPa"}
        elif sensor_type == "light":
            # Simulate light level between 0-1000 lux
            return {"value": round(random.uniform(0, 1000), 2), "unit": "lux"}
        elif sensor_type == "motion":
            # Simulate motion detection (0 or 1)
            return {"value": random.choice([0, 1]), "unit": "binary"}
        else:
            # Default random value for unknown sensor types
            return {"value": round(random.uniform(0, 100), 2), "unit": "unknown"}

    def collect_and_send_data(self):
        """Collect data from all sensors and send to database"""
        if not self.db_conn:
            raise ConnectionError("Database connection not established")

        timestamp = datetime.datetime.now()

        # Simulate occasional network/device issues
        if random.random() < 0.05:  # 5% chance of failure
            print(
                f"[{timestamp}] Device {self.device_id} - Connection error, data not sent"
            )
            return

        for sensor_type in self.sensor_types:
            reading = self.generate_reading(sensor_type)

            # Insert data into DuckDB
            self.db_conn.execute(
                """
                INSERT INTO sensor_data VALUES (?, ?, ?, ?, ?)
            """,
                (
                    timestamp,
                    self.device_id,
                    sensor_type,
                    reading["value"],
                    reading["unit"],
                ),
            )

            print(
                f"[{timestamp}] Device {self.device_id} - {sensor_type}: {reading['value']} {reading['unit']}"
            )

    def run_simulation(self, interval=5, duration=60):
        """
        Run a simulation for a specified duration

        Args:
            interval (int): Seconds between readings
            duration (int): Total duration in seconds
        """
        if not self.db_conn:
            self.connect_to_db()

        print(f"Starting simulation for device {self.device_id}")
        print(f"Sensors: {', '.join(self.sensor_types)}")
        print(f"Interval: {interval} seconds")
        print(f"Duration: {duration} seconds")

        start_time = time.time()
        end_time = start_time + duration

        while time.time() < end_time:
            self.collect_and_send_data()
            time.sleep(interval)

        print("Simulation complete")
