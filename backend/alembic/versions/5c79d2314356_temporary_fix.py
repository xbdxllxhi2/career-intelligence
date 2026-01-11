"""temporary fix

Revision ID: 5c79d2314356
Revises: a454f0ab6c17
Create Date: 2026-01-11 02:38:47.323419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c79d2314356'
down_revision: Union[str, None] = 'a454f0ab6c17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
