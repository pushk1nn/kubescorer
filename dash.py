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
    results = {"scores": scores}   # add scores up top
    t = time.time()
    for team in services:
        results[team] = {}
        for svc in services[team]:
            base = health_values[team][svc]
            if base > 2:
                if random.random() < 0.05:  # spike chance if you kept that
                    val = random.randint(7, 10)
                else:
                    val = random.randint(3, 5)
            else:
                val = 1
            results[team][svc] = val
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
    body {{
      background: #000;
      color: #00ffcc;
      font-family: monospace;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      flex-direction: column;
    }}
    h1 {{
      color: #ff00ff;
      text-align: center;
      width: 100%;
      position: absolute;
      top: 20px;
    }}
    table {{
      border-collapse: collapse;
      color: #00ffcc;
    }}
    th, td {{ padding: 10px; border: 1px solid #00ffcc; text-align: center; }}
    canvas {{ width: 120px !important; height: 60px !important; }}
  </style>
</head>
<body>
  <table id="dash"></table>

  <script>
    const services = {services_json};
    const chartOptions = {chart_options};
    const charts = {{}};

    function createTable() {{
      let html = "<tr><th>Team</th>";
      let svcNames = Object.keys(services[Object.keys(services)[0]]);
      for (let svc of svcNames) html += "<th>" + svc.toUpperCase() + "</th>";
      html += "<th>Score</th></tr>";  // Score column

      for (let team in services) {{
        html += "<tr><td><b style='color:#ff00ff'>" + team + "</b></td>";
        for (let svc in services[team]) {{
          html += "<td><canvas id='" + team + "-" + svc + "'></canvas></td>";
        }}
        html += "<td id='" + team + "-score'>0</td>";
        html += "</tr>";
      }}

      document.getElementById("dash").innerHTML = html;

      // Initialize charts after table creation
      for (let team in services) {{
        for (let svc in services[team]) {{
          let id = team + "-" + svc;
          let ctx = document.getElementById(id).getContext("2d");
          charts[id] = new Chart(ctx, {{
            type: "line",
            data: {{
              labels: Array(20).fill(""),
              datasets: [{{
                label: id,
                data: Array(20).fill(0),
                borderColor:"#00ff00",
                borderWidth:2,
                fill:false,
                tension:0.3,
                pointRadius:0
              }}]
            }},
            options: chartOptions
          }});
        }}
      }}
    }}

    async function updateCharts() {{
      const resp = await fetch("/status");
      const data = await resp.json();

      for (let team in services) {{
        for (let svc in services[team]) {{
          let id = team + "-" + svc;
          let chart = charts[id];
          let val = data[team][svc];

          chart.data.datasets[0].borderColor = val > 2 ? "#00ff00" : "#ff0033";
          chart.data.datasets[0].data.push(val);
          if (chart.data.datasets[0].data.length > 20) chart.data.datasets[0].data.shift();
          chart.update();
        }}

        // Update score cell
        if (data.scores && data.scores[team] !== undefined) {{
          document.getElementById(team + "-score").innerText = data.scores[team];
        }}
      }}
    }}

    createTable();
    setInterval(updateCharts, 1000); // slower updates
  </script>
</body>
</html>
"""
