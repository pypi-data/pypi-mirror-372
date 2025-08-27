import logging

from fastpluggy.core.global_registry import GlobalRegistry
from fastpluggy.core.widgets import TableWidget


class TableView(TableWidget):
    logging.error('[deprecated] <code>TableView</code> is deprecated; use <code>TableWidget</code>!')
    GlobalRegistry.extend_globals(
        'migration_alert',
        ['Update your <code>TableView</code> calls to use <code>TableWidget</code> instead for the new widget system benefits.']
    )
    ...