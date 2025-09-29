from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import requests
import math
import time
import random
import json

app = FastAPI()

services = {
    "team1": {"face": "32405", "synapses":"31542", "memory":"32081", "cortex":"31557", "vocals":"30546", "cyberdeck":"31886", "uplink":"30598"},
    "team2": {"face": "31526", "synapses":"32751", "memory":"30379", "cortex":"31806", "vocals":"31951", "cyberdeck":"30777", "uplink":"30213"},
}

health_values = {
    team: {svc: 1 for svc in svcs} for team, svcs in services.items()
}

scores = {
    "team1" : 0, 
    "team2" : 0,
}

# --------------------------
# Status endpoint for frontend
# --------------------------
@app.get("/status")
async def status():
    """
    Return current fluctuating values for charts.
    Healthy services wiggle, unhealthy stay flat.
    """
    results = {}
    t = time.time()
    for team in services:
        results[team] = {}
        for svc in services[team]:
            base = health_values[team][svc]
            if base > 2:  # healthy → wiggle
                fluct = math.sin(t * 3 + random.random())
                val = base + fluct
                val = max(0, min(10, val))  # clamp 0-10
                results[team][svc] = val
            else:  # unhealthy → flatline
                results[team][svc] = base
    return JSONResponse(results)


@app.post("/update")
async def update_status(request: Request):
    """
    Expected JSON payload from pods:
    {
        "team": "team1",
        "service": "face",
        "status": "ok"  # or "err"
    }
    """
    data = await request.json()
    team = data["team"]
    svc = data["service"]
    status = data["status"]

    results = {}
    # Update health_values for the chart
    if team in services and svc in services[team]:
        if status.lower() == "ok":
            # healthy → wiggle between 3–8
            health_values[team][svc] = random.randint(3, 8)
            scores[team] += 10
        else:
            # unhealthy → flatline at 1
            health_values[team][svc] = 1

    return {"message": "updated"}


# --------------------------
# Frontend
# --------------------------
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    # Use json.dumps to safely inject Python dicts into JS
    services_json = json.dumps(services)
    chart_options = json.dumps({
        "responsive": False,
        "animation": False,
        "plugins": {"legend": {"display": False}},
        "scales": {
            "x": {"display": False},
            "y": {"display": False, "min": 0, "max": 10}
        }
    })

    return f"""
<!DOCTYPE html>
<html>
<head>
  <title>Vitals</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body {{ background: #000; color: #00ffcc; font-family: monospace; }}
    h1 {{ color: #ff00ff; text-align: center; }}
    table {{ margin: auto; border-collapse: collapse; color: #00ffcc; }}
    th, td {{ padding: 10px; border: 1px solid #00ffcc; text-align: center; }}
    canvas {{ width: 120px !important; height: 60px !important; }}
  </style>
</head>
<body>
  <h1>🟢 Vitals 🟢</h1>
  <table id="dash"></table>

  <script>
    const services = {services_json};
    const chartOptions = {chart_options};
    const charts = {{}};

    function createTable() {{
      let html = "<tr><th>Team</th>";
      let svcNames = Object.keys(services[Object.keys(services)[0]]);
      for (let svc of svcNames) html += "<th>" + svc.toUpperCase() + "</th>";
      html += "</tr>";

      for (let team in services) {{
        html += "<tr><td><b style='color:#ff00ff'>" + team + "</b></td>";
        for (let svc in services[team]) {{
          html += "<td><canvas id='" + team + "-" + svc + "'></canvas></td>";
        }}
        html += "</tr>";
      }}
      document.getElementById("dash").innerHTML = html;
    }}

    function makeChart(id) {{
      let ctx = document.getElementById(id).getContext("2d");
      charts[id] = new Chart(ctx, {{
        type: "line",
        data: {{ labels: Array(20).fill(""), datasets:[{{ label: id, data: Array(20).fill(0), borderColor:"#00ff00", borderWidth:2, fill:false, tension:0.3, pointRadius:0 }}]}},
        options: chartOptions
      }});
    }}

    function initCharts() {{
      for (let team in services) for (let svc in services[team]) makeChart(team + "-" + svc);
    }}

    async function updateCharts() {{
      const resp = await fetch("/status");
      const data = await resp.json();
      for (let team in data) {{
        for (let svc in data[team]) {{
          let id = team + "-" + svc;
          let chart = charts[id];
          let val = data[team][svc];
          chart.data.datasets[0].borderColor = val > 2 ? "#00ff00" : "#ff0033";
          chart.data.datasets[0].data.push(val);
          if (chart.data.datasets[0].data.length > 20) chart.data.datasets[0].data.shift();
          chart.update();
        }}
      }}
    }}

    createTable();
    initCharts();
    setInterval(updateCharts, 200);
  </script>
</body>
</html>
"""