"""HR

Revision ID: b5e77f0bcf29
Revises: 14c2a1401d2b
Create Date: 2025-06-22 15:15:41.240494

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b5e77f0bcf29'
down_revision = '14c2a1401d2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('interns',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=64), nullable=False),
    sa.Column('internship_code', sa.String(length=64), nullable=False),
    sa.Column('completion_status', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['internship_code'], ['internships.code'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('internships', schema=None) as batch_op:
        batch_op.add_column(sa.Column('hr_profile_id', sa.String(length=64), nullable=True))
        batch_op.create_foreign_key("hr", 'profiles', ['hr_profile_id'], ['user_id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('internships', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('hr_profile_id')

    op.drop_table('interns')
    # ### end Alembic commands ###
