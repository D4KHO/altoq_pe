"""merge heads

Revision ID: a97733025ce8
Revises: 0d2d73155c00, f827759c90a9
Create Date: 2026-06-28 20:36:08.510473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a97733025ce8'
down_revision: Union[str, None] = ('0d2d73155c00', 'f827759c90a9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
