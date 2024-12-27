from fastapi import FastAPI
from lifespan import lifespan
from constants import STATUS_DELETED
from dependency import SessionDependency
from models import ORM_OBJ, ORM_CLS, Advertisement
from crud import add_item, get_item_by_id, delete_item
from schema import (GetAdvertisementResponse, CreateAdvertisementResponse, CreateAdvertisementRequest,
                    UpdateAdvertisementRequest, UpdateAdvertisementResponse,
                    StatusResponse, GetAdvertisementQueryResponse, GetAdvertisementQueryRequest)

app = FastAPI(
    title='Advertisements',
    version='0.1',
    terms_of_service='',
    lifespan=lifespan
)


@app.get('/api/v1/advertisements', response_model=GetAdvertisementResponse)
async def get_advertisements(session: SessionDependency):
    items = await session.execute(select(Advertisement))
    advertisements = items.scalar().all()
    return [adv.dict_ for adv in advertisements]


@app.post('/api/v1/advertisement', response_model=CreateAdvertisementResponse)
async def create_advertisement(session: SessionDependency, request: CreateAdvertisementRequest):
    advertisement = Advertisement(title=request.title, description=request.description,
                                  price=request.price, author=request.author)
    await add_item(session, advertisement)
    return advertisement.id_dict


@app.patch('/api/v1/advertisement/{advertisement_id}', response_model=UpdateAdvertisementResponse)
async def update_advertisement(session: SessionDependency, advertisement_id: int,
                               request: UpdateAdvertisementRequest):
    adv_json = request.model_dump(exclude_unset=True)
    adv = await get_item_by_id(session, Advertisement, advertisement_id)
    for field, value in adv_json.items():
        setattr(adv, field, value)
    await add_item(session, adv)
    return adv.id_dict


@app.delete('/api/v1/advertisement/{advertisement_id}', response_model=StatusResponse)
async def delete_advertisement(session: SessionDependency, advertisement_id: int):
    item = await get_item_by_id(session, Advertisement, advertisement_id)
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
    advertisements = items.scalars().all()
    return [adv.dict_() for adv in advertisements]

