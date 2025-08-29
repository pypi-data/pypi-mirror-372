"""Configuration settings for Taman system monitor."""

# Application metadata
APP_NAME = "Taman System Monitor"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "A system monitoring API with real-time process tracking and resource usage"

# Default server settings
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000

# CORS origins
CORS_ORIGINS = [
    "http://localhost:3000",  # Next.js dev server
    "http://127.0.0.1:3000",
]

# API settings
API_TITLE = "Taman System Monitor API"
API_DESCRIPTION = APP_DESCRIPTION
