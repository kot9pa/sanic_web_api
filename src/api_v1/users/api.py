from base64 import b64decode
from pydantic import ValidationError
from sanic import Blueprint, HTTPResponse
from sanic.log import logger
from sanic.response import json
from sanic.request import Request
from sanic_ext import openapi
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.api_v1.accounts.models import Account
from src.api_v1.transactions.models import Transaction
from .schemas import Role, UserCreate, UserUpdate
from .models import User

users = Blueprint(
    'users_blueprint', url_prefix="/users")


# TODO: Only admin
@users.post('/register')
@openapi.definition(body={
    "application/json": UserCreate
})
async def register(request: Request,
                   db_session: AsyncSession,
                   ) -> HTTPResponse:
    async with db_session.begin():
        try:
            user_create = UserCreate.model_validate(request.json)
            user = User(**user_create.model_dump(exclude_none=True))
            db_session.add(user)
            await db_session.commit()
            return json(user.to_dict(), status=201)
        except ValidationError as err:
            return json({'message': err.json()})
        except IntegrityError as err:
            return json(str(err))


@users.post('/auth')
@openapi.secured('basicAuth')
async def auth(request: Request,
               db_session: AsyncSession,
               ) -> HTTPResponse:
    async with db_session.begin():
        auth: str = request.headers.get('authorization')
        auth_decode = b64decode(auth.lstrip('Basic ')).decode()
        email, password = auth_decode.split(':')

        stmt = select(User).where(User.password == password,
                                  User.email == email)
        user = await db_session.scalar(stmt)
        if not user:
            return json({
                'error': {'message': 'Login error'}},
                status=401)

        request.ctx.session['user'] = user.id
        return json({
            'message': 'Logged in successfully',
        })


@users.get('/me')
async def get_me(request: Request,
                 db_session: AsyncSession,
                 ) -> HTTPResponse:
    async with db_session.begin():
        if not request.ctx.session:
            return json({'message': 'User is not authorized'})

        user_id = request.ctx.session['user']
        stmt = select(User).where(User.id == user_id)
        user = await db_session.scalar(stmt)
        if not user:
            return json({'message': f'{user_id=} is not found'})
        return json(user.to_dict())


@users.get('/all')
async def get_all(request: Request,
                  db_session: AsyncSession,
                  ) -> HTTPResponse:
    async with db_session.begin():
        if not request.ctx.session:
            return json({'message': 'User is not authorized'})

        user_id = request.ctx.session['user']
        stmt = select(User).where(User.id == user_id)
        user = await db_session.scalar(stmt)
        if user and user.role != Role.admin:
            return json({'message': 'User is not admin'})

        users = await db_session.scalars(select(User))
        return json([user.to_dict() for user in users.all()])


@users.get('/logout')
async def logout(request: Request):
    if not request.ctx.session:
        return json({'message': 'User is not authorized'})

    del request.ctx.session['user']
    return json({'message': 'Logged out successfully'})


# TODO: Add PATCH
@users.put('/update/<id:int>')
@openapi.definition(body={
    "application/json": UserUpdate
})
async def update(request: Request,
                 id: int,
                 db_session: AsyncSession,
                 ) -> HTTPResponse:
    async with db_session.begin():
        try:
            if not request.ctx.session:
                return json({'message': 'User is not authorized'})
            user_id = request.ctx.session['user']
            stmt = select(User).where(User.id == user_id)
            user = await db_session.scalar(stmt)
            if user.role != Role.admin:
                return json({'message': 'User is not admin'})

            user_update = UserUpdate.model_validate(request.json)
            stmt = select(User).where(User.id == id)
            user = await db_session.scalar(stmt)
            if not user:
                return json({"message": f"User id={id} not found"})

            for key, value in user_update.model_dump().items():
                setattr(user, key, value)
            await db_session.commit()
            return json(user.to_dict())
        except ValidationError as err:
            return json({'message': err.json()})
        except SQLAlchemyError as err:
            await db_session.rollback()
            raise err


@users.delete('/delete/<id:int>')
async def delete(request: Request,
                 id: int,
                 db_session: AsyncSession,
                 ) -> HTTPResponse:
    async with db_session.begin():
        if not request.ctx.session:
            return json({'message': 'User is not authorized'})
        user_id = request.ctx.session['user']
        stmt = select(User).where(User.id == user_id)
        user = await db_session.scalar(stmt)
        if user.role != Role.admin:
            return json({'message': 'User is not admin'})

        stmt = select(User).where(User.id == id)
        user = await db_session.scalar(stmt)
        if not user:
            return json({"message": f"User id={id} not found"})

        await db_session.delete(user)
        try:
            await db_session.commit()
            return json({"message": f"User id={id} deleted successfully"})
        except SQLAlchemyError as err:
            await db_session.rollback()
            raise err


@users.get('/accounts')
async def get_accounts(request: Request,
                       db_session: AsyncSession,
                       ) -> HTTPResponse:
    async with db_session.begin():
        if not request.ctx.session:
            return json({'message': 'User is not authorized'})

        user_id = request.ctx.session['user']
        stmt = select(User).where(User.id == user_id)
        user = await db_session.scalar(stmt)
        if user and user.role != Role.admin:
            stmt = select(Account).where(Account.user_id == user_id)
        else:
            stmt = select(Account).options(
                joinedload(Account.user)).order_by(Account.user_id)

        accounts = await db_session.scalars(stmt)
        return json([account.to_dict() for account in accounts.all()])


@users.get('/transactions')
async def get_transactions(request: Request,
                           db_session: AsyncSession,
                           ) -> HTTPResponse:
    async with db_session.begin():
        if not request.ctx.session:
            return json({'message': 'User is not authorized'})

        user_id = request.ctx.session['user']
        stmt = select(User).where(User.id == user_id)
        user = await db_session.scalar(stmt)
        if user and user.role != Role.admin:
            stmt = select(Transaction).where(Transaction.user_id == user_id)
        else:
            stmt = select(Transaction).options(
                joinedload(Transaction.user)).order_by(Transaction.user_id)

        transactions = await db_session.scalars(stmt)
        return json([transaction.to_dict() for transaction in transactions.all()])
