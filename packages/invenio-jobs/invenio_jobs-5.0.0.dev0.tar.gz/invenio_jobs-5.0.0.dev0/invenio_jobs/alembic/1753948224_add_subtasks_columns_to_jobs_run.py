#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Add subtasks columns to jobs_run."""

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op

# revision identifiers, used by Alembic.
revision = "1753948224"
down_revision = "1f896f6990b8"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.add_column(
        "jobs_run",
        sa.Column(
            "parent_run_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True
        ),
    )
    op.create_index(
        "ix_jobs_run_parent_run_id",
        "jobs_run",
        ["parent_run_id"],
    )
    op.add_column("jobs_run", sa.Column("total_subtasks", sa.Integer(), nullable=False))
    op.add_column(
        "jobs_run", sa.Column("completed_subtasks", sa.Integer(), nullable=False)
    )
    op.add_column(
        "jobs_run", sa.Column("failed_subtasks", sa.Integer(), nullable=False)
    )
    op.add_column(
        "jobs_run", sa.Column("errored_entries", sa.Integer(), nullable=False)
    )
    op.add_column("jobs_run", sa.Column("total_entries", sa.Integer(), nullable=False))
    op.add_column(
        "jobs_run", sa.Column("inserted_entries", sa.Integer(), nullable=False)
    )
    op.add_column(
        "jobs_run", sa.Column("updated_entries", sa.Integer(), nullable=False)
    )
    op.add_column(
        "jobs_run",
        sa.Column(
            "subtasks_closed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.create_foreign_key(
        op.f("fk_jobs_run_parent_run_id_jobs_run"),
        "jobs_run",
        "jobs_run",
        ["parent_run_id"],
        ["id"],
    )


def downgrade():
    """Downgrade database."""
    op.drop_constraint(
        op.f("fk_jobs_run_parent_run_id_jobs_run"), "jobs_run", type_="foreignkey"
    )
    op.drop_index("ix_jobs_run_parent_run_id", table_name="jobs_run")
    op.drop_column("jobs_run", "inserted_entries")
    op.drop_column("jobs_run", "updated_entries")
    op.drop_column("jobs_run", "total_entries")
    op.drop_column("jobs_run", "errored_entries")
    op.drop_column("jobs_run", "failed_subtasks")
    op.drop_column("jobs_run", "completed_subtasks")
    op.drop_column("jobs_run", "total_subtasks")
    op.drop_column("jobs_run", "subtasks_closed")
    op.drop_column("jobs_run", "parent_run_id")
