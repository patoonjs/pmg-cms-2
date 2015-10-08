"""search alerts

Revision ID: 292886e35ea7
Revises: 2e0ca9f0afc6
Create Date: 2015-10-06 11:07:25.579128

"""

# revision identifiers, used by Alembic.
revision = '292886e35ea7'
down_revision = '2e0ca9f0afc6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('search_alert',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('search', sa.String(length=255), nullable=False),
    sa.Column('content_type', sa.String(length=255), nullable=True),
    sa.Column('committee_id', sa.Integer(), nullable=True),
    sa.Column('last_alerted_at', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=True),
    sa.ForeignKeyConstraint(['committee_id'], ['committee.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_search_alert_created_at'), 'search_alert', ['created_at'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_search_alert_created_at'), table_name='search_alert')
    op.drop_table('search_alert')
    ### end Alembic commands ###
