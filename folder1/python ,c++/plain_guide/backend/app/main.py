import asyncio
from typing import Any, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .simulator import SIMULATOR


async def broadcast_loop() -> None:
    while True:
        await asyncio.sleep(1.0)
        if not SIMULATOR.simulation_active or SIMULATOR.simulation_paused:
            continue
        payload = SIMULATOR.step()
        for socket in list(getattr(SIMULATOR, "connection_pool", set())):
            try:
                await socket.send_json(payload)
            except Exception:
                pass


app = FastAPI(title="SKYGUARD AI", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    app.state.broadcast_task = asyncio.create_task(broadcast_loop())


@app.on_event("shutdown")
def shutdown_event() -> None:
    task = getattr(app.state, "broadcast_task", None)
    if task is not None:
        task.cancel()


@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "service": "SKYGUARD AI"}


@app.get("/api/flight-status")
def get_flight_status() -> Dict[str, Any]:
    return SIMULATOR.snapshot()


@app.get("/api/weather")
def get_weather() -> Dict[str, Any]:
    return SIMULATOR.snapshot()["weather"]


@app.get("/api/alerts")
def get_alerts() -> Dict[str, Any]:
    return {"alerts": SIMULATOR.alerts}


@app.post("/api/simulation/{action}")
def simulation_control(action: str) -> Dict[str, Any]:
    if action == "start":
        SIMULATOR.simulation_active = True
        SIMULATOR.simulation_paused = False
    elif action == "pause":
        SIMULATOR.simulation_paused = True
    elif action == "resume":
        SIMULATOR.simulation_paused = False
    elif action == "reset":
        SIMULATOR.__init__()
    elif action == "speedup":
        SIMULATOR.speed_multiplier = min(3.0, SIMULATOR.speed_multiplier + 0.5)
    elif action == "slowdown":
        SIMULATOR.speed_multiplier = max(0.5, SIMULATOR.speed_multiplier - 0.5)
    else:
        return {"status": "unsupported action"}
    return {"status": "ok", "simulation": {"active": SIMULATOR.simulation_active, "paused": SIMULATOR.simulation_paused, "speed": SIMULATOR.speed_multiplier}}


@app.post("/api/assistant/query")
def assistant_query(payload: Dict[str, Any]) -> Dict[str, Any]:
    prompt = str(payload.get("message", "")).lower()
    telemetry = SIMULATOR.snapshot()["telemetry"]
    if "altitude" in prompt:
        response = f"Current altitude is {telemetry['altitude']} feet and the aircraft is in the simulated {SIMULATOR.phase} phase."
    elif "weather" in prompt or "turbulence" in prompt:
        weather = SIMULATOR.snapshot()["weather"]
        response = f"Weather conditions are {weather['condition']} with {weather['wind_speed']} knots of wind and {weather['turbulence']} turbulence."
    elif "warning" in prompt:
        alerts = SIMULATOR.alerts
        if alerts and alerts[0]["severity"] != "info":
            response = alerts[0]["message"] + ": " + alerts[0]["explanation"]
        else:
            response = "No simulated warning is active at this time."
    elif "emergency" in prompt:
        response = "Follow the aircraft operating manual and review the emergency checklist references. Simulated conditions are for research use only."
    else:
        response = (
            f"The aircraft is in a simulated {SIMULATOR.phase} phase. "
            f"Indicated airspeed is {telemetry['airspeed']} knots and heading is {telemetry['heading']} degrees."
        )
    return {"response": response, "source": "rule-based AI guidance"}


@app.get("/api/session-summary")
def session_summary() -> Dict[str, Any]:
    snapshot = SIMULATOR.snapshot()
    return {
        "flight_id": "SIM-204-SKY",
        "phase": snapshot["aircraft"]["phase"],
        "destination": snapshot["telemetry"]["destination"],
        "status": snapshot["aircraft"]["flight_status"],
        "alert_count": len(snapshot["alerts"]),
        "source": "simulated telemetry",
    }


@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    if not hasattr(SIMULATOR, "connection_pool"):
        SIMULATOR.connection_pool = set()
    SIMULATOR.connection_pool.add(websocket)
    try:
        await websocket.send_json(SIMULATOR.snapshot())
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        SIMULATOR.connection_pool.discard(websocket)


@app.get("/")
def root() -> Dict[str, str]:
    return {"message": "SKYGUARD AI backend is running."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
