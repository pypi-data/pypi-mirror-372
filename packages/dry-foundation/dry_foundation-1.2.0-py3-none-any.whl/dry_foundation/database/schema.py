"""Schema-level database tools."""

from sqlalchemy import event, inspect
from sqlalchemy.schema import Column, MetaData, Table
from sqlalchemy_views import CreateView as _CreateView


class CreateView(_CreateView):
    """A simple wrapper around ``sqlalchemy_views.CreateView``."""

    def __init__(self, view, selectable):
        super().__init__(view, selectable)
        self.view_name = view.name


class ViewAwareMetaData(MetaData):
    """
    A subclass of `MetaData` that prevents automatic view creation in the database.
    """

    def create_all(self, bind=None, checkfirst=True, tables=None):
        """
        Create all known tables but exclude views.
        """
        tables = tables or self.tables.values()
        creation_tables = [table for table in tables if not isinstance(table, View)]
        super().create_all(bind=bind, checkfirst=checkfirst, tables=creation_tables)


class View(Table):
    """
    A view of the database.

    An object providing a view interface on a table. This is a subclass
    of a `sqlalchemy.sql.expression.Table` object, but which does not
    use the DDL to create the view in the database. The view is instead
    created after the engine creates the remaining tables, using the
    `ViewAwareMetaData` object to enforce the limitation on view
    creation.

    Parameters
    ----------
    name : str
        The name of the of the view.
    metadata : ViewAwareMetaData
        The metadata object that will be used by the database engine. It
        should be aware of view-like objects to prevent the DDL emission
        for creation as a table.
    selectable : sqlalchemy.sql.expression.Selectable
        The selection of columns that will comprise the view.
    *args :
        Positional arguments to be passed to the parent ``Table`` object
        constructor.
    **kwargs :
        Keyword arguments to be passed to the parent ``Table`` object
        constructor.

    Notes
    -----
    This object uses a combination of the tooling provided by the
    `sqlalchemy_views` package (https://pypi.org/project/sqlalchemy-views/),
    the SQLAlchemy wiki resource on 'Views'
    (https://github.com/sqlalchemy/sqlalchemy/wiki/Views). and the basic
    functionality of the `Table` object.
    """

    inherit_cache = True

    def __init__(self, name, metadata, selectable, *args, **kwargs):
        columns = [
            Column(column.name, column.type, primary_key=column.primary_key)
            for column in selectable.selected_columns
        ]
        super().__init__(name, metadata, *columns, *args, **kwargs)
        event.listen(
            metadata,
            "after_create",
            CreateView(self, selectable).execute_if(callable_=self._is_not_yet_view),
        )

    @staticmethod
    def _is_not_yet_view(ddl, target, connection, **kw):
        return ddl.view_name not in inspect(connection).get_view_names()
