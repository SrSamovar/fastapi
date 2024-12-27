from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from models import ORM_OBJ, ORM_CLS
from fastapi.exceptions import HTTPException


async def add_item(session: AsyncSession, item: ORM_OBJ):
    session.add(item)
    try:
        await session.commit()
    except IntegrityError:
        raise HTTPException(status_code=409, detail='record already exist')


async def delete_item(session: AsyncSession, orm_obj: ORM_OBJ):
    await session.delete(orm_obj)
    await session.commit()


async def get_item_by_id(session: AsyncSession, orm_cls: ORM_CLS, item_id: int) -> ORM_OBJ:
    orm_obj = await session.get(orm_cls, item_id)
    if orm_obj is None:
        raise HTTPException(404, 'record not found')
    return orm_obj
