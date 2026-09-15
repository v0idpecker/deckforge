"""add target_word_form to deck_cards

Revision ID: 0af0e0919db9
Revises: 7cc8d282cc7f
Create Date: 2026-09-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0af0e0919db9'
down_revision: Union[str, Sequence[str], None] = '7cc8d282cc7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('deck_cards', sa.Column('target_word_form', sa.TEXT(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('deck_cards', 'target_word_form')
