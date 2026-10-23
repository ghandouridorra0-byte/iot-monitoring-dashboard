
from datetime import datetime
from pathlib import Path
import random
import sqlite3

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="IoT Sensor Monitoring Dashboard")

# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "sensors.db"

# Create the data folder if it does not exist
DATA_DIR.mkdir(parents=True, exist_ok=True)


# Create the database table
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)


init_db()

# Serve the frontend files
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


# Simulate a sensor reading and save it

@app.get("/sensor")
def get_sensor_data():
    temperature = round(random.uniform(20, 32), 1)
    humidity = round(random.uniform(35, 75), 1)
    timestamp = datetime.now().isoformat(timespec="seconds")

    alerts = []

    if temperature >= 30:
        alerts.append("High temperature detected!")

    if humidity >= 70:
        alerts.append("High humidity detected!")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """
            INSERT INTO readings (temperature, humidity, timestamp)
            VALUES (?, ?, ?)
            """,
            (temperature, humidity, timestamp)
        )
        reading_id = cursor.lastrowid

    return {
        "id": reading_id,
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": timestamp,
        "alerts": alerts
    }



# Return the latest 20 readings, oldest first
@app.get("/history")
def get_sensor_history():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT id, temperature, humidity, timestamp
            FROM (
                SELECT id, temperature, humidity, timestamp
                FROM readings
                ORDER BY id DESC
                LIMIT 20
            )
            ORDER BY id ASC
        """).fetchall()

    return {"readings": [dict(row) for row in rows]}
