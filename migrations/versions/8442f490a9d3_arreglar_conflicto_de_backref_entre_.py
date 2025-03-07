"""arreglar conflicto de backref entre producto y venta

Revision ID: 8442f490a9d3
Revises: 717095a8ee49
Create Date: 2025-03-07 10:21:24.963665

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8442f490a9d3'
down_revision = '717095a8ee49'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('venta', schema=None) as batch_op:
        batch_op.alter_column('fecha',
               existing_type=sa.DATETIME(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('venta', schema=None) as batch_op:
        batch_op.alter_column('fecha',
               existing_type=sa.DATETIME(),
               nullable=True)

    # ### end Alembic commands ###
