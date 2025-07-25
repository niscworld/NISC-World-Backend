"""Add: User Name Model

Revision ID: c9350cf85c7b
Revises: b5e77f0bcf29
Create Date: 2025-06-22 16:15:24.904297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9350cf85c7b'
down_revision = 'b5e77f0bcf29'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_name_generation_sequence',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(length=1), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('current_users', sa.Integer(), nullable=False),
    sa.Column('next_user_number', sa.Integer(), nullable=False),
    sa.Column('total_users', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_name_generation_sequence')
    # ### end Alembic commands ###
