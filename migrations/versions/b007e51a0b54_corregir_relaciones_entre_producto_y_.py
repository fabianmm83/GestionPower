"""Corregir relaciones entre Producto y ProductoVariante

Revision ID: b007e51a0b54
Revises: 2d6de1080767
Create Date: 2025-03-09 14:28:16.243669

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b007e51a0b54'
down_revision = '2d6de1080767'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('producto', schema=None) as batch_op:
        batch_op.drop_column('variantes')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('producto', schema=None) as batch_op:
        batch_op.add_column(sa.Column('variantes', sa.TEXT(), nullable=True))

    # ### end Alembic commands ###
