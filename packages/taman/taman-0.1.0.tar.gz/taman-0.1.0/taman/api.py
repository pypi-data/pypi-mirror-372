"""FastAPI application for Taman system monitor."""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import wmi
import json
import psutil
from datetime import datetime
from .config import API_TITLE, API_DESCRIPTION, APP_VERSION, CORS_ORIGINS


def create_app():
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=APP_VERSION,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize WMI connection
    c = wmi.WMI()
    
    return app


# Create the app instance
app = create_app()


def event_stream():
    """Generate real-time system monitoring data stream."""
    while True:
        # Get system-wide stats
        # The interval makes this call wait for 1 second and calculate usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cores_percent = psutil.cpu_percent(interval=None, percpu=True)
        mem = psutil.virtual_memory()

        system_stats = {
            "cpu_usage": cpu_percent,
            "cores_usage": cores_percent,
            "memory_usage": {
                "total_gb": round(mem.total / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "percent": mem.percent,
            },
        }
        
        processes = []
        for proc in psutil.process_iter(
            ["pid", "name", "create_time", "memory_info", "num_threads"]
        ):
            try:
                runtime = (
                    datetime.now() - datetime.fromtimestamp(proc.info["create_time"])
                ).total_seconds()
                processes.append(
                    {
                        "name": proc.info["name"],
                        "pid": proc.info["pid"],
                        "runtime_seconds": runtime,
                        "ram_bytes": proc.info["memory_info"].rss,
                        "threads": proc.info["num_threads"],
                    }
                )
            except:
                continue

        # Combine everything into a single JSON payload
        payload = {"system_stats": system_stats, "processes": processes}

        yield f"data: {json.dumps(payload)}\n\n"
        # The psutil.cpu_percent(interval=1) call now handles the delay


@app.get("/kill/{pid}")
def kill_process(pid: int):
    """Terminate a process by PID."""
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        return {"status": "success", "pid": pid}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/process")
def get_processes():
    """Get current list of processes with their information."""
    processes = []
    for proc in psutil.process_iter(
        ["pid", "name", "create_time", "memory_info", "num_threads"]
    ):
        try:
            runtime = (
                datetime.now() - datetime.fromtimestamp(proc.info["create_time"])
            ).total_seconds()
            processes.append(
                {
                    "name": proc.info["name"],
                    "pid": proc.info["pid"],
                    "runtime_seconds": runtime,
                    "ram_bytes": proc.info["memory_info"].rss,
                    "threads": proc.info["num_threads"],
                }
            )
        except:
            continue
    return {"processes": processes}


@app.get("/process/stream")
def stream():
    """Stream real-time process and system data."""
    return StreamingResponse(event_stream(), media_type="text/event-stream")
