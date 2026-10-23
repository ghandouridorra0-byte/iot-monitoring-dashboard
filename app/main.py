
from datetime import datetime
from pathlib import Path
import json
import math
import sqlite3

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="IoT Sensor Monitoring Dashboard")

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "sensors.db"

DATA_DIR.mkdir(parents=True, exist_ok=True)

MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "iot-monitoring-dashboard/demo-dorra/sensors"

mqtt_client = None


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

        # Add a source column without deleting existing readings.
        columns = {
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(readings)"
            ).fetchall()
        }

        if "source" not in columns:
            conn.execute("""
                ALTER TABLE readings
                ADD COLUMN source TEXT NOT NULL DEFAULT 'legacy'
            """)


def save_reading(temperature, humidity, source):
    timestamp = datetime.now().isoformat(timespec="seconds")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            INSERT INTO readings
                (temperature, humidity, timestamp, source)
            VALUES (?, ?, ?, ?)
        """, (temperature, humidity, timestamp, source))

        return {
            "id": cursor.lastrowid,
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": timestamp,
            "source": source
        }


def on_connect(client, userdata, flags, reason_code, properties):
    if not reason_code.is_failure:
        print("MQTT connected successfully")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to: {MQTT_TOPIC}")
    else:
        print(f"MQTT connection failed: {reason_code}")


def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))

        temperature = float(payload["temperature"])
        humidity = float(payload["humidity"])

        if not math.isfinite(temperature) or not math.isfinite(humidity):
            raise ValueError("Measurements must be finite numbers")

        if not -40 <= temperature <= 80:
            raise ValueError("Temperature is outside the accepted range")

        if not 0 <= humidity <= 100:
            raise ValueError("Humidity must be between 0 and 100")

        reading = save_reading(
            temperature,
            humidity,
            "wokwi"
        )

        print(f"New Wokwi measurement: {reading}")

    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        print(f"Invalid MQTT message: {error}")


init_db()


@app.on_event("startup")
def startup_event():
    global mqtt_client

    mqtt_client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="iot-dashboard-backend"
    )

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # Keep the web API available even if MQTT is temporarily unreachable.
    mqtt_client.connect_async(
        MQTT_BROKER,
        MQTT_PORT,
        keepalive=60
    )
    mqtt_client.loop_start()


@app.on_event("shutdown")
def shutdown_event():
    if mqtt_client is not None:
        mqtt_client.disconnect()
        mqtt_client.loop_stop()


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/sensor")
def get_sensor_data():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("""
            SELECT id, temperature, humidity, timestamp, source
            FROM readings
            WHERE source = 'wokwi'
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()

    if row is None:
        raise HTTPException(
            status_code=503,
            detail="Waiting for the first Wokwi MQTT measurement"
        )

    reading = dict(row)
    alerts = []

    if reading["temperature"] >= 30:
        alerts.append("High temperature detected!")

    if reading["humidity"] >= 70:
        alerts.append("High humidity detected!")

    reading["alerts"] = alerts
    return reading


@app.get("/history")
def get_sensor_history():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT id, temperature, humidity, timestamp, source
            FROM readings
            ORDER BY id DESC
            LIMIT 20
        """).fetchall()

    return {"readings": [dict(row) for row in reversed(rows)]}
