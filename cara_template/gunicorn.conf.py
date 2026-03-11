"""
Gunicorn configuration file for CARA application.

This configuration increases the worker timeout to handle long-running
HERC risk calculations when cache is cold.
"""

# Worker timeout (in seconds)
# Default is 30, but HERC calculations can take longer on first request
timeout = 180

# Number of workers (3 workers x 4 threads = 12 concurrent request slots)
workers = 3

# Disable reload in production (enabled via CLI --reload flag for development)
reload = False

# Bind to port 5000
bind = "0.0.0.0:5000"

# Allow port reuse
reuse_port = True

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"
