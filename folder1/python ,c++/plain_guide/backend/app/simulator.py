import math
from datetime import datetime


class FlightSimulator:
    def __init__(self):
        self.simulation_active = True
        self.simulation_paused = False
        self.speed_multiplier = 1.0
        self.phase = "cruise"
        self.timestamp = 0
        self.connection_pool = set()
        self.state = {
            "altitude": 30000,
            "airspeed": 245,
            "ground_speed": 250,
            "vertical_speed": 0,
            "heading": 140,
            "pitch": 2,
            "roll": -1,
            "fuel": 78,
            "outside_temp": -20,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "destination": "KJFK",
            "departure": "KATL",
            "route_progress": 36,
            "distance_nm": 780,
        }
        self.weather = {
            "condition": "Clear",
            "wind_speed": 18,
            "wind_direction": 145,
            "visibility": 10,
            "temperature": -18,
            "turbulence": "Low",
            "warnings": [],
            "source": "Simulated weather source",
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.alerts = [
            {
                "category": "monitoring",
                "severity": "info",
                "message": "Simulated flight monitoring active.",
                "explanation": "All flight information is simulated and for research use only.",
                "recommendation": "Review current operating guidance and flight conditions.",
                "timestamp": datetime.utcnow().isoformat(),
            }
        ]

    def update_phase(self):
        altitude = self.state["altitude"]
        if altitude < 1000:
            self.phase = "ground"
        elif altitude < 8000:
            self.phase = "climb"
        else:
            self.phase = "cruise"

    def calculate_alerts(self):
        alerts = []
        if self.state["fuel"] < 25:
            alerts.append({
                "category": "fuel",
                "severity": "warning",
                "message": "Low fuel warning",
                "explanation": "Simulated fuel reserve is below the configured demonstration threshold.",
                "recommendation": "Review fuel planning and emergency checklist references.",
            })
        if abs(self.state["pitch"]) > 8:
            alerts.append({
                "category": "attitude",
                "severity": "caution",
                "message": "Unusual aircraft attitude",
                "explanation": "Pitch exceeds the configured simulated tolerance.",
                "recommendation": "Review aircraft attitude and approach guidance material.",
            })
        if abs(self.state["roll"]) > 10:
            alerts.append({
                "category": "attitude",
                "severity": "warning",
                "message": "Excessive roll deviation",
                "explanation": "Simulated roll exceeds the configured alert limits.",
                "recommendation": "Cross-check attitude indicators and flight path guidance.",
            })
        if self.weather["turbulence"] == "High":
            alerts.append({
                "category": "weather",
                "severity": "warning",
                "message": "Turbulence ahead",
                "explanation": "The simulated weather model indicates higher turbulence near the current route.",
                "recommendation": "Review the weather display and avoid unnecessary route changes in the simulation.",
            })
        return alerts or [{
            "category": "monitoring",
            "severity": "info",
            "message": "No simulated flight abnormalities detected.",
            "explanation": "The current telemetry remains within the configured demo thresholds.",
            "recommendation": "Continue flight monitoring and review weather overlays.",
        }]

    def step(self):
        if self.simulation_paused:
            return self.snapshot()

        self.timestamp += 1
        self.state["altitude"] = max(0, self.state["altitude"] + 18 * math.sin(self.timestamp / 18) + 30)
        self.state["airspeed"] = max(120, min(340, self.state["airspeed"] + math.sin(self.timestamp / 11) * 4))
        self.state["ground_speed"] = max(110, min(330, self.state["ground_speed"] + math.cos(self.timestamp / 16) * 3))
        self.state["vertical_speed"] = int(math.sin(self.timestamp / 12) * 800)
        self.state["heading"] = (self.state["heading"] + 0.8) % 360
        self.state["pitch"] = math.sin(self.timestamp / 10) * 5
        self.state["roll"] = math.cos(self.timestamp / 9) * 7
        self.state["fuel"] = max(12, self.state["fuel"] - 0.15 * self.speed_multiplier)
        self.state["outside_temp"] = -18 + math.sin(self.timestamp / 20) * 8
        self.state["latitude"] += 0.004 * math.sin(self.timestamp / 15)
        self.state["longitude"] += 0.006 * math.cos(self.timestamp / 17)
        self.state["route_progress"] = min(100, self.state["route_progress"] + 0.6)
        self.update_phase()
        self.weather["temperature"] = self.state["outside_temp"]
        self.weather["wind_speed"] = 18 + math.sin(self.timestamp / 13) * 10
        self.weather["wind_direction"] = (self.state["heading"] + 90) % 360
        self.weather["visibility"] = 9.6 + math.sin(self.timestamp / 14) * 1.2
        self.weather["turbulence"] = "Low" if self.state["altitude"] < 20000 else "Moderate" if self.state["altitude"] < 30000 else "High"
        self.weather["condition"] = "Clear" if self.weather["visibility"] > 8 else "Hazy"
        self.weather["source"] = "Simulated weather model"
        self.weather["timestamp"] = datetime.utcnow().isoformat()
        self.alerts = self.calculate_alerts()
        return self.snapshot()

    def snapshot(self):
        return {
            "aircraft": {
                "registration": "N-204SKY",
                "type": "Boeing 737-800 (simulated)",
                "flight_status": "Operational simulation",
                "phase": self.phase,
                "identification": "SKYGUARD AI - Research Flight",
            },
            "telemetry": {
                "altitude": round(self.state["altitude"], 1),
                "airspeed": round(self.state["airspeed"], 1),
                "ground_speed": round(self.state["ground_speed"], 1),
                "vertical_speed": round(self.state["vertical_speed"], 1),
                "heading": round(self.state["heading"], 1),
                "pitch": round(self.state["pitch"], 3),
                "roll": round(self.state["roll"], 3),
                "fuel": round(self.state["fuel"], 1),
                "outside_temp": round(self.state["outside_temp"], 1),
                "latitude": round(self.state["latitude"], 4),
                "longitude": round(self.state["longitude"], 4),
                "destination": self.state["destination"],
                "departure": self.state["departure"],
                "route_progress": round(self.state["route_progress"], 1),
                "distance_nm": self.state["distance_nm"],
                "timestamp": datetime.utcnow().isoformat(),
            },
            "weather": {
                "condition": self.weather["condition"],
                "wind_speed": round(self.weather["wind_speed"], 1),
                "wind_direction": round(self.weather["wind_direction"], 1),
                "visibility": round(self.weather["visibility"], 1),
                "turbulence": self.weather["turbulence"],
                "temperature": round(self.weather["temperature"], 1),
                "source": self.weather["source"],
                "timestamp": self.weather["timestamp"],
            },
            "alerts": self.alerts,
            "co_pilot": {
                "assistant_state": "Online",
                "conversation_history": [{
                    "role": "assistant",
                    "text": "The aircraft is in a simulated cruise phase with all monitoring systems active.",
                }],
            },
        }


SIMULATOR = FlightSimulator()
