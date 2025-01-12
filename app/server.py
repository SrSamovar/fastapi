from fastapi import FastAPI, HTTPException
from lifespan import lifespan
from constants import STATUS_DELETED
from dependency import SessionDependency, TokenDependency, chek_role
from auth import hash_password, check_password
from sqlalchemy import select
from models import ORM_OBJ, ORM_CLS, Advertisement, User, Token
from crud import add_item, get_item_by_id, delete_item
from schema import (GetAdvertisementResponse, CreateAdvertisementResponse, CreateAdvertisementRequest,
                    UpdateAdvertisementRequest, UpdateAdvertisementResponse,
                    StatusResponse, GetAdvertisementQueryResponse, GetAdvertisementQueryRequest,
                    LoginResponse, LoginRequest, UserResponse, UserRequest, GetUserResponse,
                    UpdateUserResponse, UpdateUserRequest)

app = FastAPI(
    title='Advertisements',
    version='0.1',
    terms_of_service='',
    lifespan=lifespan
)


@app.get('/api/v1/advertisements', response_model=GetAdvertisementResponse)
async def get_advertisements(session: SessionDependency):
    items = await session.execute(select(Advertisement))
    advertisements = items.scalars()
    return [adv.dict_ for adv in advertisements]


@app.post('/api/v1/advertisement', response_model=CreateAdvertisementResponse)
async def create_advertisement(session: SessionDependency, request: CreateAdvertisementRequest,
                               token: TokenDependency):
    if token.user.role is None:
        raise HTTPException(403, 'Access denied')
    advertisement = Advertisement(title=request.title, description=request.description,
                                  price=request.price, author=request.author, user_id=token.user.id)
    await add_item(session, advertisement)
    return advertisement.id_dict


@app.patch('/api/v1/advertisement/{advertisement_id}', response_model=UpdateAdvertisementResponse)
async def update_advertisement(session: SessionDependency, advertisement_id: int,
                               request: UpdateAdvertisementRequest, token: TokenDependency):
    adv_json = request.model_dump(exclude_unset=True)
    adv = await get_item_by_id(session, Advertisement, advertisement_id)
    await chek_role(token, adv)

    for field, value in adv_json.items():
        setattr(adv, field, value)

    await add_item(session, adv)
    return adv.id_dict


@app.delete('/api/v1/advertisement/{advertisement_id}', response_model=StatusResponse)
async def delete_advertisement(session: SessionDependency, advertisement_id: int,
                               token: TokenDependency):
    item = await get_item_by_id(session, Advertisement, advertisement_id)
    await chek_role(token, item)
    await delete_item(session, item)
    return STATUS_DELETED


@app.get('/api/v1/advertisement/{advertisement_id}', response_model=GetAdvertisementResponse,
         tags=['advertisement'])
async def get_advertisement_by_id(session: SessionDependency, advertisement_id: int):
    item = await get_item_by_id(session, Advertisement, advertisement_id)
    return item.dict_()


@app.get('/api/v1/advertisement', response_model=GetAdvertisementQueryResponse)
async def get_advertisement_by_query(session: SessionDependency, request: GetAdvertisementQueryRequest):
    query = select(Advertisement)

    if request.title:
        query = query.where(Advertisement.title.ilike(f'%{request.title}%'))
    if request.description:
        query = query.where(Advertisement.description.ilike(f'%{request.description}%'))
    if request.price is not None:
        query = query.where(Advertisement.price == request.price)
    if request.author:
        query = query.where(Advertisement.author.ilike(f'%{request.author}%'))

    items = await session.execute(query)
    advertisements = items.scalars()
    return [adv.dict_() for adv in advertisements]


@app.post('/api/v1/user', response_model=UserResponse, tags=['user'])
async def create_user(session: SessionDependency, request: UserRequest):
    request_dict = request.dict()
    request_dict['password'] = hash_password(request_dict['password'])
    user = User(**request_dict)
    await add_item(session, user)
    return user.id_dict


@app.post('/api/v1/login', response_model=LoginResponse, tags=['user'])
async def login_user(session: SessionDependency, request: LoginRequest):
    user_query = select(User).where(request.name == User.name)
    user = await session.scalar(user_query)

    if user is None:
        raise HTTPException(401, 'User name is in incorrect')
    if not check_password(request.password, user.password):
        raise HTTPException(401, 'User password is incorrect')

    token = Token(user_id=user.id)
    await add_item(session, token)
    return token.dict_


@app.get('/api/v1/user/{user_id}', response_model=GetUserResponse, tags=['user'])
async def get_user_by_id(session: SessionDependency, user_id: int):
    user = await get_item_by_id(session, User, user_id)
    return user.dict_()


@app.patch('/api/v1/user/{user_id}', response_model=UpdateUserResponse, tags=['user'])
async def update_user(session: SessionDependency, user_id: int,
                      request: UpdateUserRequest, token: TokenDependency):
    user_json = request.model_dump(exclude_unset=True)
    user = await get_item_by_id(session, User, user_id)
    await chek_role(token, user)

    for field, value in user_json.items():
        setattr(user, field, value)

    await add_item(session, user)
    return user.id_dict


@app.delete('/api/v1/user/{user_id}', response_model=StatusResponse, tags=['user'])
async def delete_user(session: SessionDependency, user_id: int, token: TokenDependency):
    user = await get_item_by_id(session, User, user_id)
    await chek_role(token, user)
    await delete_item(session, user)
    return STATUS_DELETED
