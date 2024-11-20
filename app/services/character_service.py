import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select, func

from app.models import Character, Jutsu
from app.schemas import CharacterCreate, CharacterUpdate, PageResponse
from app.schemas import JutsuCreate

logger = logging.getLogger(__name__)


class CharacterService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, character: CharacterCreate) -> Character:
        try:
            db_character = Character(**character.model_dump())
            self.session.add(db_character)
            self.session.commit()
            self.session.refresh(db_character)
            logger.info(f"Created character: {db_character.name}")
            return db_character
        except Exception as e:
            logger.error(f"Error creating character: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create character"
            )

    def get_all(
            self,
            page: int = 1,
            size: int = 10,
            search: Optional[str] = None
    ) -> PageResponse:
        try:
            query = select(Character)

            # Apply search filter
            if search:
                query = query.where(
                    Character.name.contains(search) | Character.village.contains(search)
                )

            # Default sorting by ID
            query = query.order_by(Character.id)

            # Count total items
            total = self.session.exec(
                select(func.count()).select_from(query)
            ).one()

            # Calculate pagination
            pages = (total + size - 1) // size
            offset = (page - 1) * size

            # Get items for current page
            items = self.session.exec(
                query.offset(offset).limit(size)
            ).all()

            return PageResponse(
                items=items,
                total=total,
                page=page,
                size=size,
                pages=pages,
                has_next=page < pages,
                has_prev=page > 1
            )
        except Exception as e:
            logger.error(f"Error retrieving characters: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving characters"
            )

    def get_by_id(self, character_id: int) -> Character:
        try:
            character = self.session.get(Character, character_id)
            if not character:
                logger.warning(f"Character not found: {character_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Character not found"
                )
            return character
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving character {character_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving character"
            )

    def update(self, character_id: int, character_update: CharacterUpdate) -> Character:
        try:
            db_character = self.get_by_id(character_id)

            update_data = character_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_character, key, value)

            self.session.add(db_character)
            self.session.commit()
            self.session.refresh(db_character)

            logger.info(f"Updated character: {character_id}")
            return db_character
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating character {character_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not update character"
            )

    def delete(self, character_id: int) -> None:
        try:
            character = self.get_by_id(character_id)
            self.session.delete(character)
            self.session.commit()
            logger.info(f"Deleted character: {character_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting character {character_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not delete character"
            )


    def add_jutsu(self, character_id: int, jutsu: JutsuCreate) -> Jutsu:
        try:
            # First verify the character exists
            character = self.get_by_id(character_id)

            # Create the jutsu and associate it with the character
            db_jutsu = Jutsu(**jutsu.model_dump(), character_id=character_id)
            self.session.add(db_jutsu)
            self.session.commit()
            self.session.refresh(db_jutsu)

            logger.info(f"Added jutsu {db_jutsu.name} to character {character_id}")
            return db_jutsu
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding jutsu to character {character_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not add jutsu to character"
            )
