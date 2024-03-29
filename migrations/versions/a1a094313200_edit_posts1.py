"""edit posts1

Revision ID: a1a094313200
Revises: 867571841bef
Create Date: 2024-01-08 19:39:14.729016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1a094313200'
down_revision = '867571841bef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('poster_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'users', ['poster_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('poster_id')

    # ### end Alembic commands ###
