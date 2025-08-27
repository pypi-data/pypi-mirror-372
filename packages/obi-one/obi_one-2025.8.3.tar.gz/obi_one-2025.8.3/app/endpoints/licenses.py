import logging

from entitysdk.client import Client
from entitysdk.models.morphology import License
from fastapi import APIRouter
from obi_auth import get_token
from pydantic import BaseModel

logging.basicConfig(level=logging.DEBUG)


# Define a Pydantic model for the response data
class Lic(BaseModel):
    license_label: str
    license_id: str


# Create a router for your endpoints
router = APIRouter(
    prefix="/api",
    tags=["licenses"],
)


@router.get("/licenses")
async def get_license_data() -> list[Lic]:
    entitycore_api_url = "https://staging.openbraininstitute.org/api/entitycore"

    token = get_token(environment="staging")
    client = Client(api_url=entitycore_api_url, token_manager=token)

    licenses = client.search_entity(
        entity_type=License,
        query={},
    )

    lic_list = []
    license_map = {str(s.id): s.label for s in licenses}
    for license_id, license_label in license_map.items():
        lic_list.append(Lic(license_label=license_label, license_id=license_id))

    return lic_list
