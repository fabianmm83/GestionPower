"""Cambiar precio a precio_venta y agregar costo_adquisicion

Revision ID: 8350f2ca4195
Revises: b9df71830653
Create Date: 2025-04-30 23:42:19.320779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8350f2ca4195'
down_revision = 'b9df71830653'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('producto', schema=None) as batch_op:
        batch_op.add_column(sa.Column('precio_venta', sa.Float(), nullable=False))
        batch_op.add_column(sa.Column('costo_adquisicion', sa.Float(), nullable=False))
        batch_op.drop_column('precio')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('producto', schema=None) as batch_op:
        batch_op.add_column(sa.Column('precio', sa.FLOAT(), nullable=False))
        batch_op.drop_column('costo_adquisicion')
        batch_op.drop_column('precio_venta')

    # ### end Alembic commands ###
