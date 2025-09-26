from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import requests
import random

app = FastAPI()

services = {
    "team1": {"face": "32405", "synapses":"31542", "memory":"32081", "cortex":"31557", "vocals":"30546", "cyberdeck":"31886", "uplink":"30598"},
    "team2": {"face": "31526", "synapses":"32751", "memory":"30379", "cortex":"31806", "vocals":"31951", "cyberdeck":"30777", "uplink":"30213"},
}

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
<!DOCTYPE html>
<html>
<head>
  <title>Vitals</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { background: #000; color: #00ffcc; font-family: monospace; }
    h1 { color: #ff00ff; text-align: center; }
    table { margin: auto; border-collapse: collapse; color: #00ffcc; }
    th, td { padding: 10px; border: 1px solid #00ffcc; text-align: center; }
    canvas { width: 120px !important; height: 60px !important; }
  </style>
</head>
<body>
  <h1>🟢 Vitals 🟢</h1>
  <table id="dash"></table>

  <script>
    const services = %s;
    const charts = {};

    function createTable() {
      let html = "<tr><th>Team</th>";
      let svcNames = Object.keys(services[Object.keys(services)[0]]);
      for (let svc of svcNames) {
        html += "<th>" + svc.toUpperCase() + "</th>";
      }
      html += "</tr>";

      for (let team in services) {
        html += "<tr><td><b style='color:#ff00ff'>" + team + "</b></td>";
        for (let svc in services[team]) {
          let id = team + "-" + svc;
          html += "<td><canvas id='" + id + "'></canvas></td>";
        }
        html += "</tr>";
      }
      document.getElementById("dash").innerHTML = html;
    }

    function makeChart(id, label) {
      let ctx = document.getElementById(id).getContext("2d");
      charts[id] = new Chart(ctx, {
        type: "line",
        data: {
          labels: Array(20).fill(""),
          datasets: [{
            label: label,
            data: Array(20).fill(0),
            borderColor: "#00ff00",
            borderWidth: 2,
            fill: false,
            tension: 0.3,
            pointRadius: 0,
          }]
        },
        options: {
          responsive: false,
          animation: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { display: false },
            y: { display: false, min: 0, max: 10 }
          }
        }
      });
    }

    function initCharts() {
      for (let team in services) {
        for (let svc in services[team]) {
          makeChart(team + "-" + svc, svc);
        }
      }
    }

    async function updateCharts() {
      const resp = await fetch("/status");
      const data = await resp.json();
      for (let team in data) {
        for (let svc in data[team]) {
          let id = team + "-" + svc;
          let chart = charts[id];
          let val = data[team][svc];
          let color = val > 2 ? "#00ff00" : "#ff0033";
          chart.data.datasets[0].borderColor = color;
          chart.data.datasets[0].data.push(val);
          if (chart.data.datasets[0].data.length > 20) {
            chart.data.datasets[0].data.shift();
          }
          chart.update();
        }
      }
    }

    createTable();
    initCharts();
    setInterval(updateCharts, 2000);
  </script>
</body>
</html>
""" % (services,)

@app.get("/status")
async def status():
    results = {}
    for team, svcs in services.items():
        results[team] = {}
        for svc, port in svcs.items():
            try:
                r = requests.get(f"http://127.0.0.1:{port}/healthz", timeout=1)
                ok = "ok" in r.text.lower()
            except Exception:
                ok = False

            if ok:
                # wiggle between 3–8 like a healthy heartbeat
                results[team][svc] = random.randint(3, 8)
            else:
                # flatline at a small constant value
                results[team][svc] = 1
    return JSONResponse(results)
