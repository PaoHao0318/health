"""empty message

Revision ID: b286432b3868
Revises: 785ab6aca96f
Create Date: 2024-11-27 10:37:55.112016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b286432b3868'
down_revision = '785ab6aca96f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('calories', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('protein', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('fat', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('carbs', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('carbs')
        batch_op.drop_column('fat')
        batch_op.drop_column('protein')
        batch_op.drop_column('calories')

    # ### end Alembic commands ###
