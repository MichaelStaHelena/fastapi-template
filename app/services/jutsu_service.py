import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select, func

from app.models import Jutsu, Character
from app.schemas import JutsuCreate, JutsuUpdate, PageResponse

logger = logging.getLogger(__name__)


class JutsuService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, jutsu: JutsuCreate) -> Jutsu:
        try:
            # Verify character exists if character_id is provided
            if jutsu.character_id:
                character = self.session.get(Character, jutsu.character_id)
                if not character:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Character not found"
                    )

            db_jutsu = Jutsu(**jutsu.model_dump())
            self.session.add(db_jutsu)
            self.session.commit()
            self.session.refresh(db_jutsu)
            logger.info(f"Created jutsu: {db_jutsu.name}")
            return db_jutsu
        except Exception as e:
            logger.error(f"Error creating jutsu: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create jutsu"
            )

    def get_all(
            self,
            page: int = 1,
            size: int = 10,
            search: Optional[str] = None,
            character_id: Optional[int] = None
    ) -> PageResponse:
        try:
            query = select(Jutsu)

            # Apply filters
            if search:
                query = query.where(Jutsu.name.contains(search))
            if character_id:
                query = query.where(Jutsu.character_id == character_id)

            # Default sorting by ID
            query = query.order_by(Jutsu.id)

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
            logger.error(f"Error retrieving jutsus: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving jutsus"
            )

    def get_by_id(self, jutsu_id: int) -> Jutsu:
        try:
            jutsu = self.session.get(Jutsu, jutsu_id)
            if not jutsu:
                logger.warning(f"Jutsu not found: {jutsu_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Jutsu not found"
                )
            return jutsu
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving jutsu {jutsu_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving jutsu"
            )

    def update(self, jutsu_id: int, jutsu_update: JutsuUpdate) -> Jutsu:
        try:
            db_jutsu = self.get_by_id(jutsu_id)

            # Verify character exists if character_id is being updated
            if jutsu_update.character_id is not None:
                character = self.session.get(Character, jutsu_update.character_id)
                if not character:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Character not found"
                    )

            update_data = jutsu_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_jutsu, key, value)

            self.session.add(db_jutsu)
            self.session.commit()
            self.session.refresh(db_jutsu)
            logger.info(f"Updated jutsu: {jutsu_id}")
            return db_jutsu
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating jutsu {jutsu_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not update jutsu"
            )

    def delete(self, jutsu_id: int) -> None:
        try:
            jutsu = self.get_by_id(jutsu_id)
            self.session.delete(jutsu)
            self.session.commit()
            logger.info(f"Deleted jutsu: {jutsu_id}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting jutsu {jutsu_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not delete jutsu"
            )
