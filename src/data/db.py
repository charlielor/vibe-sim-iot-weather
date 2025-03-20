# Database connection and operations
import duckdb
import os


def get_db_connection(db_path="iot_data.duckdb"):
    """Create a connection to the DuckDB database"""
    # Create the database directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # Connect to the database
    conn = duckdb.connect(db_path)

    # Create the table if it doesn't exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            timestamp TIMESTAMP,
            device_id VARCHAR,
            sensor_type VARCHAR,
            value DOUBLE,
            unit VARCHAR
        )
    """)

    return conn
