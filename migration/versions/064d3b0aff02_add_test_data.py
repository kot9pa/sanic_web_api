"""Add test data

Revision ID: 064d3b0aff02
Revises: 5a66a3540ce0
Create Date: 2025-02-24 12:37:12.012594

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.api_v1.users.schemas import Role

# revision identifiers, used by Alembic.
revision: str = '064d3b0aff02'
down_revision: Union[str, None] = '5a66a3540ce0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Create an ad-hoc table to use for the insert statement.
users_table = sa.table(
    "users",
    sa.column("id", sa.Integer),
    sa.column("email", sa.String),
    sa.column("password", sa.String),
    sa.column("fullname", sa.String),
    sa.column("role", sa.Enum(Role)),
)

accounts_table = sa.table(
    "accounts",
    sa.column("id", sa.Integer),
    sa.column("user_id", sa.Integer),
    sa.column("balance", sa.Integer),
)


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.bulk_insert(
        users_table,  # Имя вашей таблицы
        [
            {
                "id": 1,
                "email": "a1@b.c",
                "password": "password1",
                "fullname": "fullname1",
                "role": "user"
            },
            {
                "id": 2,
                "email": "a2@b.c",
                "password": "password2",
                "fullname": "fullname2",
                "role": "admin"
            },
        ],
    )
    op.bulk_insert(
        accounts_table,  # Имя вашей таблицы
        [
            {
                "id": 1,
                "user_id": 1,
                "balance": 0
            },
        ],
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DELETE FROM accounts WHERE id=1")
    op.execute("DELETE FROM users WHERE id IN (1, 2)")
    # ### end Alembic commands ###
