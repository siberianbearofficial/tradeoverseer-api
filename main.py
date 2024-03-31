from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
import alembic.config
import alembic.command

from utils.config import REDIS_HOST, REDIS_PORT, VERSION, DB_URL

from authentication.router import router as authentication_router
from users.router import router as users_router
from records.router import router as records_router
from skins.router import router as skins_router
from inventory.router import router as inventory_router
from roles.router import router as roles_router
from rarities.router import router as rarities_router
from orders.router import router as orders_router

app = FastAPI(
    title='TradeOverseer API',
    description='API for tracking prices for all items in the Standoff 2 in-game market',
    version=VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        '*'  # since the parser is running on a local machine it is impossible to know the exact origin
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get(f'/', tags=['Setup'])
async def get_root_handler():
    return {
        'data': 'TradeOverseer API',
        'detail': f'Visit /docs or /redoc for the full documentation.'
    }


@app.get('/readyz', tags=['Setup'])
async def get_readyz_handler():
    return {
        'data': 'Ready',
        'detail': 'API is ready.'
    }


@app.get('/healthz', tags=['Setup'])
async def get_healthz_handler():
    return {
        'data': 'Health',
        'detail': 'API is healthy.'
    }


@app.get('/api/v1/version', tags=['Setup'])
async def get_version_handler():
    return {
        'data': VERSION,
        'detail': 'Version was selected.'
    }


app.include_router(authentication_router, prefix='/api/v1')
app.include_router(users_router, prefix='/api/v1')
app.include_router(records_router, prefix='/api/v1')
app.include_router(skins_router, prefix='/api/v1')
app.include_router(inventory_router, prefix='/api/v1')
app.include_router(roles_router, prefix='/api/v1')
app.include_router(rarities_router, prefix='/api/v1')
app.include_router(orders_router, prefix='/api/v1')


@app.on_event('startup')
async def startup_event():
    # Redis
    try:
        redis = aioredis.from_url(f'redis://{REDIS_HOST}:{REDIS_PORT}', encoding='utf8', decode_responses=False)
        FastAPICache.init(RedisBackend(redis), prefix='tradeoverseer-api-cache')
        print('Redis Connected.')
    except Exception as e:
        print('Redis Connection Error:', e)

    # Alembic
    try:
        alembic_ini_path = Path(__file__).parent / 'migrations' / 'alembic.ini'
        alembic_config = alembic.config.Config(str(alembic_ini_path))
        alembic_config.set_main_option('sqlalchemy.url', f'{DB_URL}?async_fallback=True')
        alembic.command.upgrade(alembic_config, 'head')
        print('Alembic Revision Upgraded.')
    except Exception as e:
        print('Alembic Revision Upgrade Error:', e)
