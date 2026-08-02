"""Initial baseline with enterprise models

Revision ID: 4ef76368f703
Revises: 
Create Date: 2026-03-26 23:06:02.248714

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ef76368f703'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema. Fully bootstraps an empty database (all four tables)."""
    # ── customers ───────────────────────────────────────────────
    op.create_table('customers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(), nullable=True),
        sa.Column('tenure', sa.Integer(), nullable=True),
        sa.Column('balance', sa.Float(), nullable=True),
        sa.Column('num_products', sa.Integer(), nullable=True),
        sa.Column('has_credit_card', sa.Integer(), nullable=True),
        sa.Column('is_active_member', sa.Integer(), nullable=True),
        sa.Column('estimated_salary', sa.Float(), nullable=True),
        sa.Column('exited', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customers_customer_id'), 'customers', ['customer_id'], unique=True)
    op.create_index(op.f('ix_customers_id'), 'customers', ['id'], unique=False)

    # ── audit_log ───────────────────────────────────────────────
    op.create_table('audit_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_email', sa.String(), nullable=True),
    sa.Column('action', sa.String(), nullable=True),
    sa.Column('target', sa.String(), nullable=True),
    sa.Column('details', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_log_action'), 'audit_log', ['action'], unique=False)
    op.create_index(op.f('ix_audit_log_id'), 'audit_log', ['id'], unique=False)
    op.create_index(op.f('ix_audit_log_user_email'), 'audit_log', ['user_email'], unique=False)

    # ── customer_timeline ───────────────────────────────────────
    op.create_table('customer_timeline',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.String(), nullable=True),
    sa.Column('balance', sa.Float(), nullable=True),
    sa.Column('is_active_member', sa.Integer(), nullable=True),
    sa.Column('num_products', sa.Integer(), nullable=True),
    sa.Column('snapshot_date', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_customer_timeline_customer_id'), 'customer_timeline', ['customer_id'], unique=False)
    op.create_index(op.f('ix_customer_timeline_id'), 'customer_timeline', ['id'], unique=False)

    # ── prediction_history ──────────────────────────────────────
    op.create_table('prediction_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.String(), nullable=True),
    sa.Column('model_version', sa.String(), nullable=True),
    sa.Column('inputs', sa.JSON(), nullable=True),
    sa.Column('probability', sa.Float(), nullable=True),
    sa.Column('prediction', sa.Integer(), nullable=True),
    sa.Column('risk_level', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prediction_history_customer_id'), 'prediction_history', ['customer_id'], unique=False)
    op.create_index(op.f('ix_prediction_history_id'), 'prediction_history', ['id'], unique=False)
    op.create_index(op.f('ix_prediction_history_model_version'), 'prediction_history', ['model_version'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_prediction_history_model_version'), table_name='prediction_history')
    op.drop_index(op.f('ix_prediction_history_id'), table_name='prediction_history')
    op.drop_index(op.f('ix_prediction_history_customer_id'), table_name='prediction_history')
    op.drop_table('prediction_history')
    op.drop_index(op.f('ix_customer_timeline_id'), table_name='customer_timeline')
    op.drop_index(op.f('ix_customer_timeline_customer_id'), table_name='customer_timeline')
    op.drop_table('customer_timeline')
    op.drop_index(op.f('ix_audit_log_user_email'), table_name='audit_log')
    op.drop_index(op.f('ix_audit_log_id'), table_name='audit_log')
    op.drop_index(op.f('ix_audit_log_action'), table_name='audit_log')
    op.drop_table('audit_log')
    op.drop_index(op.f('ix_customers_customer_id'), table_name='customers')
    op.drop_index(op.f('ix_customers_id'), table_name='customers')
    op.drop_table('customers')
