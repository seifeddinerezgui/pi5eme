"""pi5eme

Revision ID: 6ac4acbffb77
Revises: 
Create Date: 2024-10-01 19:24:36.223898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '6ac4acbffb77'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_orders_id', table_name='orders')
    op.drop_index('ix_orders_symbol', table_name='orders')
    op.drop_table('orders')
    op.drop_index('ix_market_data_id', table_name='market_data')
    op.drop_index('ix_market_data_symbol', table_name='market_data')
    op.drop_table('market_data')
    op.drop_constraint('transactions_ibfk_2', 'transactions', type_='foreignkey')
    op.drop_column('transactions', 'order_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transactions', sa.Column('order_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('transactions_ibfk_2', 'transactions', 'orders', ['order_id'], ['id'])
    op.create_table('market_data',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('symbol', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('bid_price', mysql.FLOAT(), nullable=True),
    sa.Column('ask_price', mysql.FLOAT(), nullable=True),
    sa.Column('last_price', mysql.FLOAT(), nullable=True),
    sa.Column('volume', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('timestamp', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_market_data_symbol', 'market_data', ['symbol'], unique=False)
    op.create_index('ix_market_data_id', 'market_data', ['id'], unique=False)
    op.create_table('orders',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('symbol', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('order_type', mysql.VARCHAR(length=4), nullable=True),
    sa.Column('quantity', mysql.FLOAT(), nullable=True),
    sa.Column('price', mysql.FLOAT(), nullable=True),
    sa.Column('status', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('portfolio_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], name='orders_ibfk_2'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='orders_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_orders_symbol', 'orders', ['symbol'], unique=False)
    op.create_index('ix_orders_id', 'orders', ['id'], unique=False)
    # ### end Alembic commands ###