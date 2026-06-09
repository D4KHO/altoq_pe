"""estado_inicial_bd_existente

Revision ID: 0001_initial
Revises: 
Create Date: 2026-06-08 19:35:00.000000

Esta migracion representa el estado inicial de la base de datos.
Las tablas ya existian antes de implementar Alembic, asi que
esta migracion esta vacia. Sirve como punto de partida para
las migraciones futuras.

Tablas existentes:
- users
- stores
- products
- categories
- orders
- addresses
- admins
- chats
- messages
- product_templates
- template_fields
- delivery_codes
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Las tablas ya existen en la base de datos.
    # Esta migracion solo marca el punto de partida.
    pass


def downgrade() -> None:
    # No se puede revertir el estado inicial.
    pass
