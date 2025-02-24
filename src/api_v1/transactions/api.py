import hashlib
from pydantic import ValidationError
from sanic import Blueprint, HTTPResponse
from sanic.log import logger
from sanic.response import json
from sanic.request import Request
from sanic_ext import openapi
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.api_v1.transactions.schemas import TransactionCreate
from src.api_v1.accounts.models import Account
from src.api_v1.users.models import User
from src.config import settings
from .models import Transaction


transactions = Blueprint(
    'transactions_blueprint', url_prefix="/transactions")


# TODO: Only admin
@transactions.post('/create')
@openapi.definition(body={
    "application/json": TransactionCreate
})
async def create(request: Request,
                 db_session: AsyncSession,
                 ) -> HTTPResponse:
    async with db_session.begin():
        try:
            # Create transaction
            transaction_scheme = TransactionCreate.model_validate(request.json)
            transaction = Transaction(
                **transaction_scheme.model_dump(exclude_none=True))

            # Check signature
            signature = f"{transaction.account_id}{transaction.amount}{transaction.transaction_id}{transaction.user_id}{settings.SECRET_KEY}"
            signature_hash = hashlib.sha256(signature.encode())
            logger.debug(signature)
            logger.debug(signature_hash.hexdigest())
            if transaction.signature != signature_hash.hexdigest():
                return json({'message': f'Invalid {transaction.signature=}'})

            # Transaction already processed
            transaction_stmt = select(Transaction).where(
                Transaction.transaction_id == transaction.transaction_id)
            transaction_found = await db_session.scalar(transaction_stmt)
            if transaction_found:
                return json({'message': f'{transaction_found.transaction_id=} already processed'})

            # User not found
            stmt_user = select(User).where(User.id == transaction.user_id)
            stmt_account = select(Account).where(Account.id == transaction.account_id,
                                                 Account.user_id == transaction.user_id)
            user = await db_session.scalar(stmt_user)
            if not user:
                return json({'message': f'User id={transaction.user_id} not found'})

            # Create account if not exists
            account = await db_session.scalar(stmt_account)
            if not account:
                account = Account(
                    id=transaction.account_id,
                    user_id=transaction.user_id,
                    balance=transaction.amount,
                )
            else:
                account.balance += transaction.amount

            # Save to DB
            db_session.add(account)
            db_session.add(transaction)
            await db_session.commit()
            return json(transaction.to_dict(), status=201)
        except ValidationError as err:
            return json({'message': err.json()})
        except IntegrityError as err:
            return json({'message': str(err)})
