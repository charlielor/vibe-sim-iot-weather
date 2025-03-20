from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta
import os

from data.db import get_db_connection

app = Flask(
    __name__,
    template_folder=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "templates")
    ),
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "static")),
)


@app.route("/")
def index():
    """Render the main dashboard page"""
    return render_template("index.html")


@app.route("/api/devices")
def get_devices():
    """Get a list of all devices in the database"""
    conn = get_db_connection()
    devices = conn.execute("SELECT DISTINCT device_id FROM sensor_data").fetchall()
    return jsonify([device[0] for device in devices])


@app.route('/api/sensor_types')
def get_sensor_types():
    """Get a list of sensor types, optionally filtered by device"""
    device_id = request.args.get('device_id', None)
    
    conn = get_db_connection()
    
    if device_id:
        # Get sensor types for specific device
        query = """
            SELECT DISTINCT sensor_type 
            FROM sensor_data 
            WHERE device_id = ?
            ORDER BY sensor_type
        """
        sensor_types = conn.execute(query, [device_id]).fetchall()
    else:
        # Get all sensor types
        query = """
            SELECT DISTINCT sensor_type 
            FROM sensor_data 
            ORDER BY sensor_type
        """
        sensor_types = conn.execute(query).fetchall()
    
    return jsonify([sensor_type[0] for sensor_type in sensor_types]) 


@app.route("/api/data")
def get_data():
    """Get sensor data based on query parameters"""
    # Get query parameters
    device_id = request.args.get("device_id", None)
    sensor_type = request.args.get("sensor_type", None)
    hours = int(request.args.get("hours", 1))

    # Build the query
    query = "SELECT * FROM sensor_data WHERE timestamp >= ?"
    params = [datetime.now() - timedelta(hours=hours)]

    if device_id:
        query += " AND device_id = ?"
        params.append(device_id)

    if sensor_type:
        query += " AND sensor_type = ?"
        params.append(sensor_type)

    query += " ORDER BY timestamp"

    # Execute the query
    conn = get_db_connection()
    result = conn.execute(query, params).fetchdf()

    # Convert to JSON-friendly format
    data = []
    for _, row in result.iterrows():
        data.append(
            {
                "timestamp": row["timestamp"].isoformat(),
                "device_id": row["device_id"],
                "sensor_type": row["sensor_type"],
                "value": float(row["value"]),
                "unit": row["unit"],
            }
        )

    return jsonify(data)


@app.route("/api/stats")
def get_stats():
    """Get summary statistics for sensor data"""
    # Get query parameters
    device_id = request.args.get("device_id", None)
    hours = int(request.args.get("hours", 1))

    # Build the query
    query = """
        SELECT 
            sensor_type,
            COUNT(*) as count,
            MIN(value) as min,
            MAX(value) as max,
            AVG(value) as avg,
            device_id
        FROM sensor_data 
        WHERE timestamp >= ?
    """
    params = [datetime.now() - timedelta(hours=hours)]

    if device_id:
        query += " AND device_id = ?"
        params.append(device_id)

    query += " GROUP BY sensor_type, device_id"

    # Execute the query
    conn = get_db_connection()
    result = conn.execute(query, params).fetchdf()

    # Convert to JSON-friendly format
    data = []
    for _, row in result.iterrows():
        data.append(
            {
                "sensor_type": row["sensor_type"],
                "count": int(row["count"]),
                "min": float(row["min"]),
                "max": float(row["max"]),
                "avg": float(row["avg"]),
                "device_id": row["device_id"],
            }
        )

    return jsonify(data)


@app.route("/api/aggregated_data")
def get_aggregated_data():
    """Get sensor data aggregated by time granularity"""
    # Get query parameters
    device_id = request.args.get("device_id", None)
    sensor_type = request.args.get("sensor_type", None)
    hours = int(request.args.get("hours", 1))
    granularity = request.args.get("granularity", "raw")

    # Calculate the timestamp for filtering
    cutoff_time = datetime.now() - timedelta(hours=hours)

    # Build the base query
    if granularity == "raw":
        # For raw data, just return all points
        query = """
            SELECT 
                timestamp,
                device_id,
                sensor_type,
                value,
                unit
            FROM sensor_data
            WHERE timestamp >= ?
        """
    else:
        # For aggregated data, use time bucketing
        time_interval = {
            "1min": "1 minute",
            "5min": "5 minutes",
            "15min": "15 minutes",
            "30min": "30 minutes",
            "1hour": "1 hour",
        }.get(granularity, "5 minutes")

        query = f"""
            SELECT 
                time_bucket(INTERVAL '{time_interval}', timestamp) AS bucket_time,
                device_id,
                sensor_type,
                AVG(value) AS value,
                MIN(unit) AS unit
            FROM sensor_data
            WHERE timestamp >= ?
            GROUP BY bucket_time, device_id, sensor_type
            ORDER BY bucket_time
        """

    # Add filters
    params = [cutoff_time]

    if device_id:
        query += " AND device_id = ?"
        params.append(device_id)

    if sensor_type:
        query += " AND sensor_type = ?"
        params.append(sensor_type)

    # Execute the query
    conn = get_db_connection()

    try:
        # For raw data
        if granularity == "raw":
            result = conn.execute(query, params).fetchdf()

            # Convert to JSON-friendly format
            data = []
            for _, row in result.iterrows():
                data.append(
                    {
                        "timestamp": row["timestamp"].isoformat(),
                        "device_id": row["device_id"],
                        "sensor_type": row["sensor_type"],
                        "value": float(row["value"]),
                        "unit": row["unit"],
                    }
                )
        else:
            # For time-bucketed data, we need to use DuckDB's time_bucket function
            # DuckDB doesn't have a built-in time_bucket function, so we'll simulate it

            # First, get all the data
            base_query = """
                SELECT 
                    timestamp,
                    device_id,
                    sensor_type,
                    value,
                    unit
                FROM sensor_data
                WHERE timestamp >= ?
            """
            if device_id:
                base_query += " AND device_id = ?"
            if sensor_type:
                base_query += " AND sensor_type = ?"

            result = conn.execute(base_query, params).fetchdf()

            # Convert interval to seconds
            interval_map = {
                "1min": 60,
                "5min": 300,
                "15min": 900,
                "30min": 1800,
                "1hour": 3600,
            }
            interval_seconds = interval_map.get(granularity, 300)

            # Group by time bucket in Python
            if not result.empty:
                # Convert timestamp to epoch seconds and round down to nearest interval
                result["bucket"] = result["timestamp"].apply(
                    lambda x: datetime.fromtimestamp(
                        (x.timestamp() // interval_seconds) * interval_seconds
                    )
                )

                # Group by bucket, device_id, and sensor_type
                aggregated = (
                    result.groupby(["bucket", "device_id", "sensor_type"])
                    .agg({"value": "mean", "unit": "first"})
                    .reset_index()
                )

                # Convert to JSON-friendly format
                data = []
                for _, row in aggregated.iterrows():
                    data.append(
                        {
                            "timestamp": row["bucket"].isoformat(),
                            "device_id": row["device_id"],
                            "sensor_type": row["sensor_type"],
                            "value": float(row["value"]),
                            "unit": row["unit"],
                        }
                    )
            else:
                data = []

        return jsonify(data)

    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return jsonify({"error": str(e)}), 500


def run_app():
    """Run the Flask application"""
    app.run(debug=True)
