from sanic import Blueprint

from src.config import settings
from src.api_v1.users.api import users
from src.api_v1.accounts.api import accounts
from src.api_v1.transactions.api import transactions
from src.api_v1.users.models import User
from src.api_v1.accounts.models import Account
from src.api_v1.transactions.models import Transaction

__all__ = (
    "User",
    "Account",
    "Transaction",
)

api = Blueprint.group(users,
                      accounts,
                      transactions,
                      url_prefix=settings.api_v1_prefix)
