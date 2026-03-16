"""
Database helpers for the extracted runtime core.
"""

from __future__ import annotations

from collections.abc import Mapping

from . import state

MAXINT = (2 ** 31) - 1


def _ini_getboolean(section, option, default=False):
    if not state.ini:
        return default
    try:
        return state.ini.getboolean(section, option, default)
    except TypeError:
        return state.ini.getboolean(section, option, fallback=default)
    except Exception:
        return default


def _is_mapping_row(row):
    return isinstance(row, Mapping)


def dictfetchone(cursor):
    """
    Return one row from a cursor as a dict.
    Assume the column names are unique.
    """
    row = cursor.fetchone()
    if row is None:
        return None
    if _is_mapping_row(row):
        return row
    if not getattr(cursor, "description", None):
        return row
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    rows = cursor.fetchall()
    if not rows:
        return rows
    if _is_mapping_row(rows[0]):
        return rows
    if not getattr(cursor, "description", None):
        return rows
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def query(querystring, *args):
    """general query. yields rows from query"""
    cursor = state.db.cursor()
    cursor.execute(querystring, *args)
    results = dictfetchall(cursor)
    cursor.close()
    yield from results


def changeq(querystring, *args):
    """general inset/update. no return"""
    cursor = state.db.cursor()
    try:
        cursor.execute(querystring, *args)
    except Exception:
        state.db.rollback()
        raise
    state.db.commit()
    terug = cursor.rowcount
    cursor.close()
    return terug


def insertta(querystring, *args):
    """
    insert ta
    from insert get back the idta; this is different with postgrSQL.
    """
    cursor = state.db.cursor()
    cursor.execute(querystring, *args)
    newidta = cursor.lastrowid if hasattr(cursor, "lastrowid") else 0
    if not newidta:
        cursor.execute("""SELECT lastval() as idta""")
        newidta = dictfetchone(cursor)["idta"]
    state.db.commit()
    cursor.close()
    return newidta


def unique_runcounter(domain, updatewith=None):
    """as unique, but per run of bots-engine."""
    domain += 'bots_1_8_4_9_6'
    nummer = getattr(state, domain, 0)
    if updatewith is None:
        nummer += 1
        updatewith = nummer
        if updatewith > MAXINT:
            updatewith = 0
    setattr(state, domain, updatewith)
    return nummer


def unique(domein, updatewith=None):
    """
    generate unique number within range domain. Uses db to keep track of last generated number.
    """
    if _ini_getboolean('acceptance', 'runacceptancetest', False):
        return unique_runcounter(domein)

    cursor = state.db.cursor()
    try:
        cursor.execute(
            """SELECT nummer FROM uniek WHERE domein=%(domein)s""",
            {'domein': domein}
        )
        nummer = dictfetchone(cursor)["nummer"]
        if updatewith is None:
            nummer += 1
            updatewith = nummer
            if updatewith > MAXINT:
                updatewith = 0
        cursor.execute(
            """UPDATE uniek SET nummer=%(nummer)s WHERE domein=%(domein)s""",
            {"domein": domein, "nummer": updatewith},
        )
    except TypeError:
        cursor.execute(
            """INSERT INTO uniek (domein,nummer) VALUES (%(domein)s,1)""",
            {"domein": domein}
        )
        nummer = 1
    state.db.commit()
    cursor.close()
    return nummer


def checkunique(domein, receivednumber):
    """
    to check if received number is sequential: value is compare with new generated number.
    if domain not used before, initialize it . '1' is the first value expected.
    """
    newnumber = unique(domein)
    if newnumber == receivednumber:
        return True

    if _ini_getboolean('acceptance', 'runacceptancetest', False):
        return False

    changeq(
        """UPDATE uniek SET nummer=%(nummer)s WHERE domein=%(domein)s""",
        {'domein': domein, 'nummer': newnumber - 1},
    )
    return False


def set_database_lock():
    try:
        changeq("""INSERT INTO mutex (mutexk) VALUES (1)""")
    except Exception:
        return False
    return True


def remove_database_lock():
    changeq("""DELETE FROM mutex WHERE mutexk=1""")
