import base64

from fastapi import APIRouter, Depends, HTTPException

from vt4ai.api.auth import get_api_key
from vt4ai.api.config import shared_template_loader
from vt4ai.constants.output_formats import AvailableFormats
from vt4ai.services.vt_service import VTService

urls_router = APIRouter(
    prefix="/urls",
)


@urls_router.get("/{url}")
async def get_url_report(
    url: str,
    format: AvailableFormats = AvailableFormats.JSON,
    api_key: str = Depends(get_api_key),
):
    """Get URL report from VirusTotal using the provided API key. Make sure to pass the URL encoded in base64."""
    try:
        decoded_url = base64.b64decode(url.encode("ascii"))
        service = VTService(api_key, shared_template_loader)
        report = await service.get_url_report(decoded_url, format)
        if format == AvailableFormats.JSON:
            return {"data": report}
        else:
            return {"data": report, "format": format.value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
