"""add topic table

Revision ID: 3f71198e49b7
Revises: 688062f46329
Create Date: 2017-05-12 13:48:04.022667

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3f71198e49b7'
down_revision = '688062f46329'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('estimators_ibfk_1', 'estimators', type_='foreignkey')
    op.drop_column('estimators', 'dataset_id')
    op.add_column('topics', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'topics', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'topics', type_='foreignkey')
    op.drop_column('topics', 'user_id')
    op.add_column('estimators', sa.Column('dataset_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('estimators_ibfk_1', 'estimators', 'datasets', ['dataset_id'], ['id'])
    # ### end Alembic commands ###
