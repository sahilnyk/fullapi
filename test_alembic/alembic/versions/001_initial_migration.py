"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-05-11 14:26:14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create initial tables
    pass


def downgrade() -> None:
    # Drop all tables
    pass
