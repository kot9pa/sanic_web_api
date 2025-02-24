import os
import sys
from sanic import Sanic
from sanic.log import logger
from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from sanic_session import AIORedisSessionInterface, Session
from src.api_v1 import api
from src.database import Database
from src.config import settings

app = Sanic("Sanic_Web_Api")
app.config.update(settings.model_dump())
app.blueprint(api)
session = Session()


@app.before_server_start
async def setup_connections(application: Sanic, _) -> None:
    # logger.debug(application.config)
    logger.debug("Initialize connection to Redis")
    redis_client = aioredis.from_url(settings.get_redis_url(),
                                     decode_responses=True)
    logger.debug(f"Ping successful: {await redis_client.ping()}")

    # init extensions fabrics
    session.init_app(
        app, interface=AIORedisSessionInterface(redis_client))

    logger.debug("Initialize connection to PostgreSQL")
    db_conn = Database(echo=settings.DB_ECHO)
    db_session: AsyncSession = db_conn.create_session()

    # Adding DIs
    application.ext.dependency(db_session)
    application.ext.dependency(redis_client)

app.ext.openapi.add_security_scheme(
    "basicAuth",
    "http",
    scheme="basic",
)

if __name__ == '__main__':
    app.run(host=settings.SERVER_HOST, 
            port=settings.SERVER_PORT)
