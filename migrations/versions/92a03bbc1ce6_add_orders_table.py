"""Add orders table

Revision ID: 92a03bbc1ce6
Revises: b286432b3868
Create Date: 2024-11-27 10:53:50.694996

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92a03bbc1ce6'
down_revision = 'b286432b3868'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('menu_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('calories', sa.Float(), nullable=False),
    sa.Column('protein', sa.Float(), nullable=False),
    sa.Column('fat', sa.Float(), nullable=False),
    sa.Column('carbs', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['menu_id'], ['menus.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('order')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('menu_id', sa.INTEGER(), nullable=False),
    sa.Column('quantity', sa.INTEGER(), nullable=False),
    sa.Column('calories', sa.FLOAT(), nullable=True),
    sa.Column('protein', sa.FLOAT(), nullable=True),
    sa.Column('fat', sa.FLOAT(), nullable=True),
    sa.Column('carbs', sa.FLOAT(), nullable=True),
    sa.ForeignKeyConstraint(['menu_id'], ['menus.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('orders')
    # ### end Alembic commands ###
