"""Add unique contraint for attachment user/file_id

Revision ID: 3231d2c623bc
Revises: 75a62b74b239
Create Date: 2025-05-14 06:08:15.425495

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3231d2c623bc"
down_revision: Union[str, None] = "75a62b74b239"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("attachment", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            batch_op.f("uq_attachment_user_account_id"),
            ["user_account_id", "legacy_file_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("attachment", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("uq_attachment_user_account_id"), type_="unique"
        )
