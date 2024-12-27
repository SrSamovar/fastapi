from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import Depends


async def get_session() -> AsyncSession:
    with Session() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session)]

