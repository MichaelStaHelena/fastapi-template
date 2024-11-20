from typing import Optional

from fastapi import APIRouter, Depends, Query, Path, status
from fastapi.params import Body

from app.dependencies import get_character_service, get_jutsu_service
from app.schemas import (
    CharacterCreate, CharacterRead, CharacterUpdate,
    JutsuCreate, JutsuRead, JutsuUpdate,
    PageResponse, PageParams
)
from app.services.character_service import CharacterService
from app.services.jutsu_service import JutsuService

# Create routers with tags for better API documentation
character_router = APIRouter(prefix="/characters", tags=["characters"])
jutsu_router = APIRouter(prefix="/jutsus", tags=["jutsus"])


# Character Routes
@character_router.post(
    "/",
    response_model=CharacterRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new character",
    response_description="The created character"
)
async def create_character(
        character: CharacterCreate,
        service: CharacterService = Depends(get_character_service)
):
    """
    Create a new Naruto character with the following information:

    - **name**: required, character name
    - **village**: required, village of the character
    - **rank**: optional, rank of the character
    """
    return service.create(character)


@character_router.get(
    "/",
    response_model=PageResponse,
    summary="Get all characters",
    response_description="Paginated list of characters"
)
async def read_characters(
        page_params: PageParams = Depends(),
        search: Optional[str] = Query(
            None,
            min_length=3,
            max_length=50,
            description="Search characters by name or village"
        ),
        service: CharacterService = Depends(get_character_service)
):
    """
    Get all Naruto characters with pagination and search.

    Parameters:
    - **page**: Page number (starts from 1)
    - **size**: Number of items per page
    - **search**: Optional search term for name or village
    """
    return service.get_all(
        page=page_params.page,
        size=page_params.size,
        search=search
    )


@character_router.get(
    "/{character_id}",
    response_model=CharacterRead,
    summary="Get a specific character",
    response_description="The requested character"
)
async def read_character(
        character_id: int = Path(..., ge=1),
        service: CharacterService = Depends(get_character_service)
):
    """
    Get a specific Naruto character by their ID.

    - **character_id**: The ID of the character to retrieve
    """
    return service.get_by_id(character_id)


@character_router.patch(
    "/{character_id}",
    response_model=CharacterRead,
    summary="Update a character",
    response_description="The updated character"
)
async def update_character(
        character_id: int,
        character_update: CharacterUpdate,
        service: CharacterService = Depends(get_character_service)
):
    """
    Update a Naruto character with the following information:

    - **character_id**: The ID of the character to update
    - **name**: optional, new character name
    - **village**: optional, new village
    - **rank**: optional, new rank
    """
    return service.update(character_id, character_update)


@character_router.delete(
    "/{character_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a character",
    response_description="Character successfully deleted"
)
async def delete_character(
        character_id: int = Path(..., ge=1),
        service: CharacterService = Depends(get_character_service)
):
    """
    Delete a specific Naruto character by their ID.

    - **character_id**: The ID of the character to delete
    """
    service.delete(character_id)

@character_router.post(
    "/{character_id}/jutsus",
    response_model=JutsuRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a jutsu to a character",
    response_description="The created jutsu"
)
async def add_jutsu_to_character(
    character_id: int = Path(..., ge=1),
    jutsu: JutsuCreate = Body(...),
    service: CharacterService = Depends(get_character_service)
):
    """
    Add a new jutsu to a specific character.

    - **character_id**: The ID of the character
    - **jutsu**: The jutsu data to create and associate
    """
    return service.add_jutsu(character_id, jutsu)

# Jutsu Routes
@jutsu_router.post(
    "/",
    response_model=JutsuRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new jutsu",
    response_description="The created jutsu"
)
async def create_jutsu(
        jutsu: JutsuCreate,
        service: JutsuService = Depends(get_jutsu_service)
):
    """
    Create a new jutsu with the following information:

    - **name**: required, jutsu name
    - **type**: required, jutsu type (Ninjutsu, Taijutsu, etc.)
    - **chakra_cost**: required, chakra cost
    - **character_id**: optional, the ID of the associated character
    """
    return service.create(jutsu)


@jutsu_router.get(
    "/",
    response_model=PageResponse,
    summary="Get all jutsus",
    response_description="Paginated list of jutsus"
)
async def read_jutsus(
        page_params: PageParams = Depends(),
        search: Optional[str] = Query(
            None,
            min_length=3,
            max_length=50,
            description="Search jutsus by name"
        ),
        service: JutsuService = Depends(get_jutsu_service)
):
    """
    Get all jutsus with pagination and search.

    Parameters:
    - **page**: Page number (starts from 1)
    - **size**: Number of items per page
    - **search**: Optional search term for jutsu name
    """
    return service.get_all(
        page=page_params.page,
        size=page_params.size,
        search=search
    )


@jutsu_router.get(
    "/{jutsu_id}",
    response_model=JutsuRead,
    summary="Get a specific jutsu",
    response_description="The requested jutsu"
)
async def read_jutsu(
        jutsu_id: int = Path(..., ge=1),
        service: JutsuService = Depends(get_jutsu_service)
):
    """
    Get a specific jutsu by its ID.

    - **jutsu_id**: The ID of the jutsu to retrieve
    """
    return service.get_by_id(jutsu_id)


@jutsu_router.patch(
    "/{jutsu_id}",
    response_model=JutsuRead,
    summary="Update a jutsu",
    response_description="The updated jutsu"
)
async def update_jutsu(
        jutsu_id: int,
        jutsu_update: JutsuUpdate,
        service: JutsuService = Depends(get_jutsu_service)
):
    """
    Update a jutsu with the following information:

    - **jutsu_id**: The ID of the jutsu to update
    - **name**: optional, new jutsu name
    - **type**: optional, new jutsu type
    - **chakra_cost**: optional, new chakra cost
    - **character_id**: optional, new character association
    """
    return service.update(jutsu_id, jutsu_update)


@jutsu_router.delete(
    "/{jutsu_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a jutsu",
    response_description="Jutsu successfully deleted"
)
async def delete_jutsu(
        jutsu_id: int = Path(..., ge=1),
        service: JutsuService = Depends(get_jutsu_service)
):
    """
    Delete a specific jutsu by its ID.

    - **jutsu_id**: The ID of the jutsu to delete
    """
    service.delete(jutsu_id)
