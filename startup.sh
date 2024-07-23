# Start the worker in the background
python watchdog_workers.py &&

# Start the main application
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
