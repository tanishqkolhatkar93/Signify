from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from backend.app.schemas.sign import SignManifest, SignItem, ReverseMatchRequest, ReverseMatchResponse
from backend.app.services.sign_dictionary.manifest_service import dictionary_service

router = APIRouter(prefix="/signs", tags=["Sign Dictionary"])

@router.get("", response_model=List[SignItem])
def list_signs(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search query")
):
    if search:
        return dictionary_service.search_signs(search)
    return dictionary_service.list_signs(category=category)

@router.get("/manifest", response_model=SignManifest)
def get_manifest():
    return dictionary_service.get_manifest()

@router.get("/{sign_id}", response_model=SignItem)
def get_sign(sign_id: str):
    sign = dictionary_service.get_sign_by_id(sign_id)
    if not sign:
        raise HTTPException(status_code=404, detail=f"Sign '{sign_id}' not found in supported vocabulary.")
    return sign

@router.post("/reverse-match", response_model=ReverseMatchResponse)
def reverse_match(req: ReverseMatchRequest):
    return dictionary_service.match_reverse_phrase(req.phrase)

