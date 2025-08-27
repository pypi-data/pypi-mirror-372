"""Helper objects to improve the modularity of tests."""

from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey, ForeignKeyConstraint

from dry_foundation import DryFlask, Factory
from dry_foundation.database.models import AuthorizedAccessMixin, Model
from dry_foundation.database.schema import View


@Factory
def create_test_app(config=None):
    # Create and configure the test app
    app = DryFlask("test", "Test Application")
    app.configure(config)
    return app


class Entry(Model):
    __tablename__ = "entries"
    # Columns
    x: Mapped[int] = mapped_column(primary_key=True)
    y: Mapped[str]
    user_id: Mapped[int]
    # Relationships
    authorized_entries: Mapped[list["AuthorizedEntry"]] = relationship(
        back_populates="entry", cascade="all, delete-orphan"
    )


class AuthorizedEntry(AuthorizedAccessMixin, Model):
    __tablename__ = "authorized_entries"
    _user_id_join_chain = (Entry,)
    # Columns
    a: Mapped[int] = mapped_column(primary_key=True)
    b: Mapped[str | None]
    c: Mapped[int] = mapped_column(ForeignKey("entries.x"))
    # Relationships
    entry: Mapped["Entry"] = relationship(back_populates="authorized_entries")
    alt_auth_entries: Mapped[list["AlternateAuthorizedEntry"]] = relationship(
        back_populates="auth_entry", cascade="all, delete-orphan"
    )


class AlternateAuthorizedEntry(AuthorizedAccessMixin, Model):
    __tablename__ = "alt_authorized_entries"
    _user_id_join_chain = (AuthorizedEntry, Entry)
    # Columns
    p: Mapped[int] = mapped_column(primary_key=True)
    q: Mapped[int] = mapped_column(ForeignKey("authorized_entries.a"))
    # Relationships
    auth_entry: Mapped["AuthorizedEntry"] = relationship(
        back_populates="alt_auth_entries"
    )
    view: Mapped["AlternateAuthorizedEntryView"] = relationship(
        back_populates="alt_auth_entry",
        uselist=False,
        viewonly=True,
    )


class AlternateAuthorizedEntryView(AuthorizedAccessMixin, Model):
    # Use the hybrid declarative style for the view
    __table__ = View(
        "alt_authorized_entries_view",
        Model.metadata,
        select(
            AlternateAuthorizedEntry.p.label("p"),
            AlternateAuthorizedEntry.q.label("q"),
            (AlternateAuthorizedEntry.p + AlternateAuthorizedEntry.q).label("r"),
        ),
        ForeignKeyConstraint(["p"], ["alt_authorized_entries.p"]),
    )
    _user_id_join_chain = (AlternateAuthorizedEntry, AuthorizedEntry, Entry)
    # Relationships
    alt_auth_entry: Mapped["AlternateAuthorizedEntry"] = relationship(
        back_populates="view",
        viewonly=True,
    )
