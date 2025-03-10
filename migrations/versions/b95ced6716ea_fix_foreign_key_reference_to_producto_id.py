"""Fix foreign key reference to producto.id

Revision ID: b95ced6716ea
Revises: 27b822bfca00
Create Date: 2025-03-09 02:35:38.237062

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b95ced6716ea'
down_revision = '27b822bfca00'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('movimiento_inventario')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('movimiento_inventario',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('producto_id', sa.INTEGER(), nullable=False),
    sa.Column('tipo', sa.VARCHAR(length=10), nullable=False),
    sa.Column('cantidad', sa.INTEGER(), nullable=False),
    sa.Column('fecha', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['producto_id'], ['producto.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
