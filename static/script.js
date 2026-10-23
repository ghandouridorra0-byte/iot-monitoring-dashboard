
let sensorChart;

async function updateSensorData() {
    const message = document.getElementById("message");

    try {
        const response = await fetch("/sensor");

        if (!response.ok) {
            throw new Error("Unable to retrieve sensor data");
        }

        const data = await response.json();

        document.getElementById("temperature").textContent =
            data.temperature;

        document.getElementById("humidity").textContent =
            data.humidity;

        document.getElementById("timestamp").textContent =
            new Date(data.timestamp).toLocaleString();

        message.textContent = "Sensor data loaded successfully.";
        message.style.color = "#16a34a";

        await updateChart();

    } catch (error) {
        message.textContent = "Unable to connect to the API.";
        message.style.color = "#dc2626";
        console.error(error);
    }
}

async function updateChart() {
    const response = await fetch("/history");

    if (!response.ok) {
        throw new Error("Unable to load sensor history");
    }

    const result = await response.json();
    const readings = result.readings;

    const labels = readings.map(reading =>
        new Date(reading.timestamp).toLocaleTimeString()
    );

    const temperatures = readings.map(reading =>
        reading.temperature
    );

    const humidities = readings.map(reading =>
        reading.humidity
    );

    if (!sensorChart) {
        const context = document
            .getElementById("sensorChart")
            .getContext("2d");

        sensorChart = new Chart(context, {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Temperature (°C)",
                        data: temperatures,
                        borderColor: "#2563eb",
                        backgroundColor: "rgba(37, 99, 235, 0.1)",
                        tension: 0.3
                    },
                    {
                        label: "Humidity (%)",
                        data: humidities,
                        borderColor: "#16a34a",
                        backgroundColor: "rgba(22, 163, 74, 0.1)",
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    } else {
        sensorChart.data.labels = labels;
        sensorChart.data.datasets[0].data = temperatures;
        sensorChart.data.datasets[1].data = humidities;
        sensorChart.update();
    }
}

updateSensorData();
setInterval(updateSensorData, 5000);

const alertsBox = document.getElementById("alerts");

if (data.alerts && data.alerts.length > 0) {
    alertsBox.className = "alerts warning";
    alertsBox.textContent = data.alerts.join(" ");
} else {
    alertsBox.className = "alerts";
    alertsBox.textContent =
        "No alerts. All values are within the configured limits.";
}
