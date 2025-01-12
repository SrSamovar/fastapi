import datetime
import uuid
from sqlalchemy import select
from models import Session, Token
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi import Depends, Header, HTTPException
from models import TOKEN_TTL_SEC


async def get_session() -> AsyncSession:
    with Session() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session)]


async def get_token(
        x_token: Annotated[uuid.UUID, Header()],
        session: SessionDependency):
    token_query = select(Token).where(x_token == Token.token,
                                      Token.created_at >= datetime.datetime.now() - datetime.timedelta(
                                          seconds=TOKEN_TTL_SEC)
                                      )
    token = await session.scalar(token_query)

    if token is None:
        raise HTTPException(401, 'invalid token')

    return token


TokenDependency = Annotated[Token, Depends(get_token)]


async def chek_role(token, item):
    if token.user_id != item.user_id or token.user.role != 'admin':
        raise HTTPException(403, 'Access denied')
