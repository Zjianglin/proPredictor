"""add estimator user_id

Revision ID: 0db4d63e3ba7
Revises: f563a661137b
Create Date: 2017-05-13 17:02:42.818905

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0db4d63e3ba7'
down_revision = 'f563a661137b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('estimators', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'estimators', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'estimators', type_='foreignkey')
    op.drop_column('estimators', 'user_id')
    # ### end Alembic commands ###
