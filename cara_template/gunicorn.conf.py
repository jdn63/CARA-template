"""
Gunicorn configuration file for CARA application.

This configuration increases the worker timeout to handle long-running
HERC risk calculations when cache is cold.
"""
import os

# Worker timeout (in seconds)
# Default is 30, but HERC calculations can take longer on first request
timeout = 180

# Number of workers (2 workers x 4 threads = 8 concurrent request slots)
workers = 2

# Use threaded workers
threads = 4

# Preload the app before forking workers to share memory and reduce
# per-worker startup DB connections
preload_app = True

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

def post_fork(server, worker):
    """Mark worker ID so only worker 0 starts the scheduler."""
    os.environ["GUNICORN_WORKER_ID"] = str(worker.age)
