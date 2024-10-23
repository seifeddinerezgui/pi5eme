"""added lesson model

Revision ID: 899fcfae59bf
Revises: a82a21b744ee
Create Date: 2024-10-21 22:02:19.241879

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '899fcfae59bf'
down_revision: Union[str, None] = 'a82a21b744ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_lesson',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('lesson_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_foreign_key(None, 'assets', 'portfolios', ['portfolio_id'], ['id'])
    op.create_foreign_key(None, 'portfolios', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'transactions', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.drop_constraint(None, 'portfolios', type_='foreignkey')
    op.drop_constraint(None, 'assets', type_='foreignkey')
    op.drop_table('user_lesson')
    # ### end Alembic commands ###
