"""topic fix chart filed length

Revision ID: 47810986823c
Revises: addc83e6c855
Create Date: 2017-05-14 23:28:34.895533

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '47810986823c'
down_revision = 'addc83e6c855'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('chart', table_name='topics')
    op.drop_column('topics', 'chart')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('topics', sa.Column('chart', mysql.VARCHAR(length=64), nullable=True))
    op.create_index('chart', 'topics', ['chart'], unique=True)
    # ### end Alembic commands ###