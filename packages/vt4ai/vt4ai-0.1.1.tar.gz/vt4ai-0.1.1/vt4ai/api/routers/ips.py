from fastapi import APIRouter, Depends, HTTPException

from vt4ai.api.auth import get_api_key
from vt4ai.api.config import shared_template_loader
from vt4ai.constants.output_formats import AvailableFormats
from vt4ai.services.vt_service import VTService

ips_router = APIRouter(
    prefix="/ips",
)


@ips_router.get("/{ip}")
async def get_ip_report(
    ip: str,
    format: AvailableFormats = AvailableFormats.JSON,
    api_key: str = Depends(get_api_key),
):
    """Get IP report from VirusTotal using the provided API key."""
    try:
        service = VTService(api_key, shared_template_loader)
        report = await service.get_ip_report(ip, format)
        if format == AvailableFormats.JSON:
            return {"data": report}
        else:
            return {"data": report, "format": format.value}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving IP report: {str(e)}")
