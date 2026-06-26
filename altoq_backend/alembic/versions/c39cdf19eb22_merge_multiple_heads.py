"""merge multiple heads

Revision ID: c39cdf19eb22
Revises: acf6d1fb3036, de436e7154f1
Create Date: 2026-06-24 21:01:12.192255

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c39cdf19eb22'
down_revision: Union[str, None] = ('acf6d1fb3036', 'de436e7154f1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
