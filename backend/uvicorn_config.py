"""
Uvicorn configuration with increased WebSocket timeout
"""

# Uvicorn configuration
ws_ping_interval = 60  # Send WebSocket pings every 60 seconds
ws_ping_timeout = 120  # Wait 120 seconds for pong before closing
timeout_keep_alive = 120  # Keep HTTP connections alive for 120 seconds
