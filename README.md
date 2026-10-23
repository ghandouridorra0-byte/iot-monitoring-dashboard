\# IoT Monitoring Dashboard



A software-based IoT monitoring system using simulated sensor data, MQTT communication, FastAPI, SQLite, and Docker.



\## Features

\- ESP32 and DHT22 simulation using Wokwi

\- MQTT communication

\- FastAPI backend

\- SQLite data storage

\- Temperature and humidity monitoring

\- Sensor history and alerts

\- Web dashboard with HTML, CSS, JavaScript, and Chart.js

\- Docker containerization



\## Architecture

Wokwi (ESP32 + DHT22) → MQTT Broker → FastAPI → SQLite → Web Dashboard



\## Technologies

Python, FastAPI, MQTT, SQLite, HTML, CSS, JavaScript, Chart.js, Docker, Wokwi.



\## Run with Docker

```bash

docker build -t iot-monitoring-dashboard .

docker run -d -p 8090:8000 --name iot-dashboard -v iot\_data:/app/data iot-monitoring-dashboard

```



Open the dashboard at: http://127.0.0.1:8090/



\## API Endpoints

\- `/` — Dashboard

\- `/sensor` — Latest sensor reading

\- `/history` — Sensor history

\- `/docs` — API documentation

lien de simulation wokwi:https://wokwi.com/projects/478702709025485825

