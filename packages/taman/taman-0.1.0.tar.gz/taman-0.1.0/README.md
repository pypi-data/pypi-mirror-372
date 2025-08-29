# Taman - System Monitoring API

Taman is a FastAPI-based system monitoring tool that provides real-time process tracking and resource usage information through RESTful endpoints and Server-Sent Events (SSE).

## Features

- **Real-time system monitoring**: CPU usage, memory consumption, and process information
- **Process management**: Kill processes by PID
- **Streaming data**: Real-time updates via Server-Sent Events
- **Cross-platform**: Works on Windows, macOS, and Linux
- **REST API**: Clean and simple API endpoints
- **CORS support**: Ready for web frontend integration

## Installation

Install from PyPI:

```bash
pip install taman
```

Or install from source:

```bash
git clone https://github.com/yourusername/taman
cd taman
pip install -e .
```

## Quick Start

### Running the API server

```bash
# Start the server
taman

# Or run directly with Python
python -m taman.main
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `GET /process` - Get current processes list
- `GET /process/stream` - Stream real-time system data (SSE)
- `GET /kill/{pid}` - Terminate a process by PID

### Example Usage

```python
import requests

# Get current processes
response = requests.get("http://localhost:8000/process")
processes = response.json()

# Kill a process
response = requests.get("http://localhost:8000/kill/1234")
```

### Streaming Data Example

```javascript
// JavaScript example for consuming SSE stream
const eventSource = new EventSource('http://localhost:8000/process/stream');

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('System Stats:', data.system_stats);
    console.log('Processes:', data.processes);
};
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/taman
cd taman

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black taman/

# Lint code
flake8 taman/
```

### Running in Development Mode

```bash
# Run with auto-reload
uvicorn taman.main:app --reload --host 0.0.0.0 --port 8000
```

## Data Format

### System Stats Response

```json
{
  "system_stats": {
    "cpu_usage": 15.2,
    "cores_usage": [12.1, 18.3, 14.7, 16.8],
    "memory_usage": {
      "total_gb": 16.0,
      "used_gb": 8.5,
      "percent": 53.1
    }
  },
  "processes": [
    {
      "name": "python.exe",
      "pid": 1234,
      "runtime_seconds": 3600.5,
      "ram_bytes": 52428800,
      "threads": 8
    }
  ]
}
```

## Requirements

- Python 3.8+
- FastAPI
- psutil
- uvicorn
- wmi (Windows only)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues, please file a bug report on the [GitHub Issues](https://github.com/yourusername/taman/issues) page.