"""empty message

Revision ID: 6277ac8e2c75
Revises: dc60c86baafd
Create Date: 2022-08-13 01:12:58.644806

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6277ac8e2c75'
down_revision = 'dc60c86baafd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('show',
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], ),
    sa.PrimaryKeyConstraint('venue_id', 'artist_id', 'show_id')
    )
    # ### end Alembic commands ###
   

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('show')
    # ### end Alembic commands ###
