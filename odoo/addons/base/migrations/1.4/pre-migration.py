# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

import psycopg2

from odoo.tools import SQL
from odoo.tools.sql import drop_depending_views

_logger = logging.getLogger(__name__)


def _alter_column_to_bigint(cr, table, column):
    query = SQL(
        "ALTER TABLE %s ALTER COLUMN %s TYPE bigint",
        SQL.identifier(table), SQL.identifier(column),
    )
    try:
        with cr.savepoint(flush=False):
            cr.execute(query, log_exceptions=False)
    except psycopg2.NotSupportedError:
        drop_depending_views(cr, table, column)
        cr.execute(query)


def migrate(cr, version):
    """ Convert the int4 "id" primary keys, their sequences and the foreign
    keys referencing them to bigint (int8).

    32-bit primary keys can be exhausted by long-lived databases, as in the
    quay.io outage of May 2025: the primary key of one of its tables reached
    the maximum value of a 32-bit integer, making any INSERT fail.
    """
    # "id" primary keys and their sequences
    cr.execute("""
        SELECT c.relname
          FROM pg_class c
          JOIN pg_attribute a ON a.attrelid = c.oid AND a.attname = 'id'
         WHERE c.relkind = 'r'
           AND c.relnamespace = 'public'::regnamespace
           AND a.atttypid = 'int4'::regtype
           AND a.attinhcount = 0
      ORDER BY c.relname
    """)
    tables = [row[0] for row in cr.fetchall()]
    for table in tables:
        # migrate the id sequence first, keeping the column default
        # (nextval) working on the whole bigint range
        cr.execute(SQL("SELECT pg_get_serial_sequence(%s, 'id')", table))
        sequence = cr.fetchone()[0]
        if sequence:
            cr.execute(SQL("ALTER SEQUENCE %s AS BIGINT", SQL.identifier(*sequence.split('.'))))
        # PostgreSQL cannot change the type of an inherited column when the
        # not-null constraint names differ between parent and children (e.g.
        # the ir_actions family); detach the children tables, migrate each
        # table apart, then reattach them
        cr.execute(
            "SELECT inhrelid::regclass::text FROM pg_inherits WHERE inhparent = %s::regclass",
            [table],
        )
        children = [row[0] for row in cr.fetchall()]
        for child in children:
            cr.execute(SQL(
                "ALTER TABLE %s NO INHERIT %s",
                SQL.identifier(child), SQL.identifier(table),
            ))
            _alter_column_to_bigint(cr, child, 'id')
        _alter_column_to_bigint(cr, table, 'id')
        for child in children:
            cr.execute(SQL(
                "ALTER TABLE %s INHERIT %s",
                SQL.identifier(child), SQL.identifier(table),
            ))

    # int4 columns with a foreign key constraint (many2one and many2many
    # relation columns); inherited columns (attinhcount > 0) are converted
    # by the recursive ALTER of their parent table
    cr.execute("""
        SELECT DISTINCT con.conrelid::regclass::text, a.attname
          FROM pg_constraint con
          JOIN pg_attribute a ON a.attrelid = con.conrelid AND a.attnum = ANY(con.conkey)
         WHERE con.contype = 'f'
           AND a.atttypid = 'int4'::regtype
           AND a.attinhcount = 0
      ORDER BY 1, 2
    """)
    for table, column in cr.fetchall():
        _alter_column_to_bigint(cr, table, column)

    _logger.info("Migrated %d tables to bigint id primary keys", len(tables))
