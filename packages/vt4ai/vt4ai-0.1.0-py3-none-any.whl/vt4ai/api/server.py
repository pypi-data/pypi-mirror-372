import uvicorn
from fastapi import FastAPI

from vt4ai.api.config import shared_template_loader
from vt4ai.api.routers.domains import domains_router
from vt4ai.api.routers.files import files_router
from vt4ai.api.routers.ips import ips_router
from vt4ai.api.routers.urls import urls_router

app = FastAPI(
    title="VT4AI API Server",
    description="API Server for VT4AI",
    version="0.1.0",
)


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "VT4AI API Server"}


@app.get("/templates", tags=["VT4AI"])
def get_available_templates():
    return shared_template_loader.get_templates_summary()


app.include_router(files_router, prefix="/api/v1", tags=["Files"])
app.include_router(urls_router, prefix="/api/v1", tags=["URLs"])
app.include_router(domains_router, prefix="/api/v1", tags=["Domains"])
app.include_router(ips_router, prefix="/api/v1", tags=["IPs"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
