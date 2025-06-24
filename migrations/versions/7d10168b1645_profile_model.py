"""Profile Model

Revision ID: 7d10168b1645
Revises: 9d5809ba754d
Create Date: 2025-06-24 11:17:14.927209
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7d10168b1645'
down_revision = '9d5809ba754d'
branch_labels = None
depends_on = None

def upgrade():
    # Drop unique constraint on 'email'
    with op.batch_alter_table('profiles', schema=None) as batch_op:
        # batch_op.drop_constraint('uq_profiles_email', type_='unique')
        batch_op.add_column(sa.Column('gender', sa.String(length=20), nullable=True))

def downgrade():
    # Re-create unique constraint on 'email'
    with op.batch_alter_table('profiles', schema=None) as batch_op:
        batch_op.drop_column('gender')
        # batch_op.create_unique_constraint('uq_profiles_email', ['email'])
