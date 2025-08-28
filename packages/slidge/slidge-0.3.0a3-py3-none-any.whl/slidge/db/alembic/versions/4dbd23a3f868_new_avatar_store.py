"""New avatar store

Revision ID: 4dbd23a3f868
Revises: 04cf35e3cf85
Create Date: 2025-04-14 21:57:49.030430

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4dbd23a3f868"
down_revision: Union[str, None] = "04cf35e3cf85"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # a bug in slidge v0.3.0alpha0 lead to a crash during this migration which ended up with
    # this temporary  tables in here
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_avatar;")
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_contact;")

    with op.batch_alter_table("avatar", schema=None) as batch_op:
        batch_op.add_column(sa.Column("legacy_id", sa.String(), nullable=True))
        batch_op.create_unique_constraint("avatar_unique_legacy_id", ["legacy_id"])

    batch_op.execute("""
        UPDATE avatar
        SET legacy_id = contact.avatar_legacy_id
        FROM contact
        WHERE avatar.id = contact.avatar_id
    """)

    batch_op.execute("""
        UPDATE avatar
        SET legacy_id = room.avatar_legacy_id
        FROM room
        WHERE avatar.id = room.avatar_id
    """)

    # the following 4 OPs have been added manually because somewhere before, we messed up
    # and the client_type server side default value was pc (no quote) instead of "pc"
    op.execute(
        """
        CREATE TABLE contact_new (
            id INTEGER NOT NULL,
            user_account_id INTEGER NOT NULL,
            legacy_id VARCHAR NOT NULL,
            jid TEXT NOT NULL,
            avatar_id INTEGER,
            nick VARCHAR,
            cached_presence BOOLEAN NOT NULL,
            last_seen DATETIME,
            ptype VARCHAR,
            pstatus VARCHAR,
            pshow VARCHAR,
            is_friend BOOLEAN NOT NULL,
            added_to_roster BOOLEAN NOT NULL,
            extra_attributes VARCHAR,
            updated BOOLEAN NOT NULL,
            caps_ver VARCHAR,
            vcard VARCHAR,
            vcard_fetched BOOLEAN DEFAULT 1 NOT NULL,
            avatar_legacy_id VARCHAR,
            client_type VARCHAR(8) DEFAULT 'pc' NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(user_account_id) REFERENCES user_account (id),
            FOREIGN KEY(avatar_id) REFERENCES avatar (id),
            UNIQUE (user_account_id, legacy_id) CONSTRAINT uq_user_account_legacy_id,
            UNIQUE (user_account_id, jid) CONSTRAINT uq_user_account_jid
        );
        """
    )

    op.execute(
        """
        INSERT INTO contact_new (id, user_account_id, legacy_id, jid, avatar_id, nick, cached_presence, last_seen, ptype, pstatus, pshow, is_friend, added_to_roster, extra_attributes, updated, caps_ver, vcard, vcard_fetched, avatar_legacy_id, client_type)
        SELECT id, user_account_id, legacy_id, jid, avatar_id, nick, cached_presence, last_seen, ptype, pstatus, pshow, is_friend, added_to_roster, extra_attributes, updated, caps_ver, vcard, vcard_fetched, avatar_legacy_id, client_type
        FROM contact;
        """
    )
    op.execute("DROP TABLE contact;")
    op.execute("ALTER TABLE contact_new RENAME TO contact;")

    with op.batch_alter_table("contact", schema=None) as batch_op:
        batch_op.drop_column("avatar_legacy_id")

    with op.batch_alter_table("room", schema=None) as batch_op:
        batch_op.drop_column("avatar_legacy_id")


def downgrade() -> None:
    with op.batch_alter_table("room", schema=None) as batch_op:
        batch_op.add_column(sa.Column("avatar_legacy_id", sa.VARCHAR(), nullable=True))

    with op.batch_alter_table("contact", schema=None) as batch_op:
        batch_op.add_column(sa.Column("avatar_legacy_id", sa.VARCHAR(), nullable=True))

    with op.batch_alter_table("avatar", schema=None) as batch_op:
        batch_op.drop_constraint("avatar_unique_legacy_id", type_="unique")
        batch_op.drop_column("legacy_id")
