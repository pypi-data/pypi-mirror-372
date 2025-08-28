import warnings

try:
    import psycopg2
    import fastapi
    import multipart
    import httpx
    import uvicorn
except ModuleNotFoundError:
    warnings.warn("Missing optional dependencies to use the HTTP API. Install them with `pip install sunpeek [api]`")
