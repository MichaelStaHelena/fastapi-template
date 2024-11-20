from fastapi import Depends
from sqlmodel import Session

from app.database import get_session
from app.services.character_service import CharacterService
from app.services.jutsu_service import JutsuService


def get_character_service(
        session: Session = Depends(get_session)
) -> CharacterService:
    return CharacterService(session)


def get_jutsu_service(
        session: Session = Depends(get_session)
) -> JutsuService:
    return JutsuService(session)
