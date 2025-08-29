# example_usage.py
from htmllogger import log, info, debug, warning, error, report_exception, config
import random
import time

# Configure logger
config(
    max_files=5,
    max_size=1000000,
    log_dir="example_logs",
    main_filename="example.html"
)

# Simulate different application components


def database_operation():
    log("Connecting to database", tag="database", color="cyan")
    info("Executing query", tag="database")
    time.sleep(0.1)
    if random.random() > 0.8:
        warning("Slow query performance", tag="performance")
    log("Database operation completed", tag="database", color="cyan")


def authentication():
    log("Authentication started", tag="auth", color="blue")
    info("Verifying credentials", tag="auth")
    time.sleep(0.05)
    if random.random() > 0.9:
        error("Invalid credentials", tag="auth")
    log("Authentication completed", tag="auth", color="blue")


def processing_task():
    log("Task started", tag="processing", color="green")
    for i in range(5):
        debug(f"Processing step {i}", tag="processing")
        time.sleep(0.02)
    log("Task completed", tag="processing", color="green")


# Main execution
log("Application simulation started", tag="system", color="green")

for i in range(10):
    info(f"Starting iteration {i}", tag="system")

    # Simulate different operations
    database_operation()
    authentication()
    processing_task()

    # Random error simulation
    if random.random() > 0.7:
        try:
            raise ValueError("Simulated random error")
        except Exception as e:
            report_exception(e, timeout=0.1)

log("Application simulation completed", tag="system", color="green")
info("All operations finished", tag="system")
