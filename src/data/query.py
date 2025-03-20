import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def query_recent_data(db_path="iot_data.duckdb", hours=1):
    """Query the most recent data from the database"""
    conn = duckdb.connect(db_path)

    # Calculate the timestamp for filtering
    cutoff_time = datetime.now() - timedelta(hours=hours)

    # Query the data
    result = conn.execute(
        """
        SELECT * FROM sensor_data
        WHERE timestamp >= ?
        ORDER BY timestamp
    """,
        (cutoff_time,),
    ).fetchdf()

    return result


def plot_sensor_data(data, sensor_type):
    """Plot data for a specific sensor type"""
    # Filter data for the specified sensor type
    sensor_data = data[data["sensor_type"] == sensor_type]

    if sensor_data.empty:
        print(f"No data found for sensor type: {sensor_type}")
        return

    # Get the unit for this sensor type
    unit = sensor_data["unit"].iloc[0]

    # Create a figure
    plt.figure(figsize=(10, 6))

    # Group by device_id and plot each device separately
    for device_id, device_data in sensor_data.groupby("device_id"):
        plt.plot(device_data["timestamp"], device_data["value"], label=device_id)

    plt.title(f"{sensor_type.capitalize()} Readings")
    plt.xlabel("Time")
    plt.ylabel(f"{sensor_type.capitalize()} ({unit})")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Format the x-axis to show readable timestamps
    plt.gcf().autofmt_xdate()

    # Show the plot
    plt.show()


def generate_summary_stats(data):
    """Generate summary statistics for all sensor types"""
    if data.empty:
        return pd.DataFrame()

    # Group by device_id and sensor_type
    summary = (
        data.groupby(["device_id", "sensor_type"])
        .agg({"value": ["min", "max", "mean", "std", "count"]})
        .reset_index()
    )

    # Flatten the multi-level columns
    summary.columns = ["device_id", "sensor_type", "min", "max", "mean", "std", "count"]

    return summary


def detect_anomalies(data, sensor_type, z_threshold=3.0):
    """Detect anomalies in sensor data using Z-score"""
    if data.empty:
        return None

    # Filter for the specific sensor type
    sensor_data = data[data["sensor_type"] == sensor_type].copy()

    if sensor_data.empty:
        return None

    # Calculate Z-scores
    mean = sensor_data["value"].mean()
    std = sensor_data["value"].std()

    if std == 0:
        return None

    sensor_data["z_score"] = (sensor_data["value"] - mean) / std

    # Identify anomalies
    anomalies = sensor_data[abs(sensor_data["z_score"]) > z_threshold]

    return anomalies
