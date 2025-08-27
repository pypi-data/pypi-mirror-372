from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from vt4ai.api.auth import get_api_key
from vt4ai.api.config import shared_template_loader
from vt4ai.constants.output_formats import AvailableFormats
from vt4ai.services.vt_service import VTService

files_router = APIRouter(
    prefix="/files",
)


@files_router.get("/{file_hash}")
async def get_file_report(
    file_hash: str,
    format: AvailableFormats = AvailableFormats.JSON,
    api_key: str = Depends(get_api_key),
):
    """Get file report from VirusTotal using the provided API key."""
    try:
        service = VTService(api_key, shared_template_loader)
        report = await service.get_file_report(file_hash, format)
        if format == AvailableFormats.JSON:
            return {"data": report}
        else:
            return {"data": report, "format": format.value}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving file report: {str(e)}")


@files_router.get("/relationships/types")
def get_relationship_types():
    """Get all available file relationship types."""
    try:
        relationships = VTService.get_relationship_types()
        return {"relationships": relationships}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving relationship types: {str(e)}",
        )


@files_router.get("/{file_hash}/relationships/{relationship}")
async def get_file_report_with_relationships(
    file_hash: str,
    relationship: str,
    format: AvailableFormats = AvailableFormats.JSON,
    template_name: Optional[str] = None,
    limit: int = 10,
    cursor: Optional[str] = None,
    api_key: str = Depends(get_api_key),
):
    """Get a file report including related objects by relationship type."""
    try:
        service = VTService(api_key, shared_template_loader)
        result = await service.get_file_report_with_relationships_descriptors(
            file_hash=file_hash,
            relationship=relationship,
            format=format,
            template_name=template_name,
            limit=limit,
            cursor=cursor,
        )
        if format == AvailableFormats.JSON:
            return {"data": result}
        else:
            return {"data": result, "format": format.value}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving file relationships: {str(e)}"
        )
