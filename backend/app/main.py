import asyncio
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.validate_input.manual_data import PredictionInput
from app.database import save_entry, get_entries, get_entry, create_tables_entries
from app.predict import predict
from app.iot_generator import generator

# Create FastAPI app
app = FastAPI(
    title="Desalination Prediction & IoT Stream API",
    description="API for predicting plant performance and streaming synthetic IoT telemetry",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WebSocket] Client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"[WebSocket] Client disconnected. Remaining clients: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

# Stream state configuration
stream_state = {
    "is_active": True,
    "interval_seconds": 3.0,
    "task": None
}

async def background_iot_stream():
    """Background task continuously broadcasting synthetic IoT telemetry to WebSocket subscribers."""
    while True:
        try:
            if stream_state["is_active"] and len(manager.active_connections) > 0:
                payload = generator.generate_and_predict()
                await manager.broadcast({
                    "event": "telemetry_tick",
                    "data": payload
                })
            await asyncio.sleep(stream_state["interval_seconds"])
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[IoT Stream Error] {e}")
            await asyncio.sleep(stream_state["interval_seconds"])

@app.on_event("startup")
async def startup_event():
    create_tables_entries()
    stream_state["task"] = asyncio.create_task(background_iot_stream())
    print("[IoT Stream] Background generator started.")

@app.on_event("shutdown")
async def shutdown_event():
    if stream_state["task"]:
        stream_state["task"].cancel()
    print("[IoT Stream] Background generator stopped.")

@app.websocket("/ws/iot")
async def websocket_iot_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial immediate tick upon client connection
        initial_tick = generator.generate_and_predict()
        await websocket.send_json({
            "event": "connected",
            "message": "Connected to Desalination IoT Telemetry Stream",
            "data": initial_tick
        })

        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                if data == "ping":
                    await websocket.send_json({"event": "pong"})
            except asyncio.TimeoutError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[WebSocket Error] {e}")
        manager.disconnect(websocket)

# IoT Control & REST Endpoints
@app.post("/iot/tick")
async def trigger_iot_tick():
    """Trigger an instant synthetic IoT telemetry reading, run ML prediction, save to DB, and broadcast."""
    try:
        payload = generator.generate_and_predict()
        await manager.broadcast({
            "event": "telemetry_tick",
            "data": payload
        })
        return {
            "status": "success",
            "data": payload
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating IoT tick: {str(e)}")

@app.post("/iot/start")
async def start_iot_stream():
    """Start or resume automatic background IoT telemetry streaming."""
    stream_state["is_active"] = True
    return {"status": "streaming_started", "interval_seconds": stream_state["interval_seconds"]}

@app.post("/iot/stop")
async def stop_iot_stream():
    """Pause automatic background IoT telemetry streaming."""
    stream_state["is_active"] = False
    return {"status": "streaming_paused"}

@app.post("/iot/config")
async def config_iot_stream(interval_seconds: float = 3.0):
    """Update background streaming interval frequency."""
    if interval_seconds < 0.5:
        raise HTTPException(status_code=400, detail="Interval must be at least 0.5 seconds")
    stream_state["interval_seconds"] = interval_seconds
    return {"status": "config_updated", "interval_seconds": stream_state["interval_seconds"]}

###############################################################################

# Existing REST Endpoints
@app.post("/predict-and-save")
async def predict_and_save(data: PredictionInput):
    try:
        entry_data = {
            'operator_id': data.operator_id,
            'feed_flowrate': data.Feed_Flowrate_m3h,
            'feed_tds': data.Feed_TDS_ppm,
            'feed_salinity': data.Feed_Salinity_gL,
            'temperature': data.Feed_Temperature_C,
            'recovery': data.Recovery_percent,
            'flux': data.Flux_LMH,
            'pressure_drop': data.Pressure_Drop_bar
        }
        
        input_data = {
            'Feed Flowrate (m3/h)': data.Feed_Flowrate_m3h,
            'Feed TDS (ppm)': data.Feed_TDS_ppm,
            'Feed Salinity (g/L)': data.Feed_Salinity_gL,
            'Feed Temperature (°C)': data.Feed_Temperature_C,
            'Recovery (%)': data.Recovery_percent,
            'Flux (LMH)': data.Flux_LMH,
            'Pressure Drop (bar)': data.Pressure_Drop_bar
        }
        
        result = predict(input_data)

        entry_data['permeate_flowrate'] = result['flowrate']
        entry_data['permeate_tds'] = result['tds']
        entry_data['status'] = result['status']

        entry_id = save_entry(entry_data)
        
        return {
            "entry_id": entry_id,
            "prediction": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/entries")
async def list_entries():
    try:
        entries = get_entries()
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/entry/{entry_id}")
async def retrieve_entry(entry_id: int):
    try: 
        entry = get_entry(entry_id)
        return entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")