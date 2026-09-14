"""create users, authors, and books tables

Revision ID: 001_initial
Revises:
Create Date: 2026-09-14
"""

from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "authors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_authors_id", "authors", ["id"])
    op.create_index("ix_authors_name", "authors", ["name"], unique=True)

    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["authors.id"]),
    )
    op.create_index("ix_books_id", "books", ["id"])
    op.create_index("ix_books_title", "books", ["title"])
    op.create_index("ix_books_author_id", "books", ["author_id"])


def downgrade() -> None:
    op.drop_index("ix_books_author_id", table_name="books")
    op.drop_index("ix_books_title", table_name="books")
    op.drop_index("ix_books_id", table_name="books")
    op.drop_table("books")
    op.drop_index("ix_authors_name", table_name="authors")
    op.drop_index("ix_authors_id", table_name="authors")
    op.drop_table("authors")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
