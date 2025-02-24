from pydantic import ValidationError
from sanic import Blueprint, HTTPResponse
from sanic.log import logger
from sanic.response import json
from sanic.request import Request
from sanic_ext import openapi
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.api_v1.accounts.schemas import AccountCreate
from src.api_v1.accounts.models import Account
from src.api_v1.users.models import User


accounts = Blueprint(
    'accounts_blueprint', url_prefix="/accounts")


# TODO: Only admin
@accounts.post('/create')
@openapi.definition(body={
    "application/json": AccountCreate
})
async def create(request: Request,
                 db_session: AsyncSession,
                 ) -> HTTPResponse:
    async with db_session.begin():
        try:
            account_create = AccountCreate.model_validate(request.json)
            stmt = select(User).where(User.id == account_create.user_id)
            user = await db_session.scalar(stmt)
            if not user:
                return json({'message': f'User id={account_create.user_id} not found'})

            account = Account(**account_create.model_dump(exclude_none=True))
            db_session.add(account)
            await db_session.commit()
            return json(account.to_dict(), status=201)
        except ValidationError as err:
            return json({'message': err.json()})
        except IntegrityError as err:
            return json({'message': str(err)})
