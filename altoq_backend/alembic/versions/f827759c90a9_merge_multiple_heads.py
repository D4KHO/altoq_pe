"""merge multiple heads

Revision ID: f827759c90a9
Revises: 2ccfc7173f75, c39cdf19eb22
Create Date: 2026-06-26 02:20:32.188069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f827759c90a9'
down_revision: Union[str, None] = ('2ccfc7173f75', 'c39cdf19eb22')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
