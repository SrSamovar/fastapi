import datetime
import uuid
from custom_types import Role
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy import Integer, String, Boolean, DateTime, func, UUID, ForeignKey, CheckConstraint
import os

POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'LSamovar69')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'aiohttp')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

DSN = (f'postgresql+asyncpg://'
       f'{POSTGRES_USER}:{POSTGRES_PASSWORD}@'
       f'{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')

engine = create_async_engine(DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):

    @property
    def id_dict(self):
        return {'id': self.id}


class User(Base):
    __tablename__ = 'user'
    __tableargs__ = (CheckConstraint('role in ("user", "admin")'))

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    tokens: Mapped[list['Token']] = relationship("Token", lazy='joined', back_populates='user')
    advertisements: Mapped[list['Advertisement']] = relationship('Advertisement',
                                                                 lazy='joined',
                                                                 back_populates='user')
    role: Mapped[Role] = mapped_column(String, default='user')


class Token(Base):
    __tablename__ = 'token'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    token: Mapped[uuid.UUID] = mapped_column(UUID,
                                             unique=True,
                                             server_default=func.gen_random_uuid())
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped[User] = relationship(User, lazy='joined', back_populates='tokens')

    @property
    def dict_(self):
        return {'token': self.token}


class Advertisement(Base):
    __tablename__ = 'advertisement'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    user: Mapped[User] = relationship(User, lazy='joined', back_populates='advertisements')

    @property
    def dict_(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'author': self.author,
            'created_at': self.created_at.isoformat()
        }


ORM_OBJ = Advertisement | User | Token
ORM_CLS = type[Advertisement] | type[User] | type[Token]


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()
