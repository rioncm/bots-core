"""
Routing and confirmation helpers for the extracted runtime core.
"""

from __future__ import annotations

from . import state
from .constants import FILEOUT, OK
from .db import changeq, query


def globalcheckconfirmrules(confirmtype):
    """Check whether this confirmation type is configured at all."""
    for confirmdict in state.confirmrules:
        if confirmdict['confirmtype'] == confirmtype:
            return True
    return False


def checkconfirmrules(confirmtype, **kwargs):
    # pylint: disable=too-many-branches
    confirm = False
    for confirmdict in state.confirmrules:
        if confirmdict['confirmtype'] != confirmtype:
            continue
        if confirmdict['ruletype'] == 'all':
            confirm = not confirmdict['negativerule']
        elif confirmdict['ruletype'] == 'confirmasked':
            if kwargs.get('confirmasked') and confirmtype.startswith('send-'):
                confirm = not confirmdict['negativerule']
        elif confirmdict['ruletype'] == 'route':
            if 'idroute' in kwargs and confirmdict['idroute'] == kwargs['idroute']:
                confirm = not confirmdict['negativerule']
        elif confirmdict['ruletype'] == 'channel':
            if 'idchannel' in kwargs and confirmdict['idchannel'] == kwargs['idchannel']:
                confirm = not confirmdict['negativerule']
        elif confirmdict['ruletype'] == 'frompartner':
            if 'frompartner' in kwargs and confirmdict['frompartner'] == kwargs['frompartner']:
                confirm = not confirmdict['negativerule']
        elif confirmdict['ruletype'] == 'topartner':
            if 'topartner' in kwargs and confirmdict['topartner'] == kwargs['topartner']:
                confirm = not confirmdict['negativerule']
        elif confirmdict['ruletype'] == 'messagetype':
            if 'messagetype' in kwargs and confirmdict['messagetype'] == kwargs['messagetype']:
                confirm = not confirmdict['negativerule']
    return confirm


def lookup_translation(frommessagetype, fromeditype, alt, frompartner, topartner):
    """
    Lookup the translation:
    frommessagetype, fromeditype, alt, frompartner, topartner ->
    mappingscript, tomessagetype, toeditype
    """
    for row in query(
        """SELECT tscript,tomessagetype,toeditype
            FROM translate
            WHERE frommessagetype = %(frommessagetype)s
            AND fromeditype = %(fromeditype)s
            AND active=%(booll)s
            AND (alt='' OR alt=%(alt)s)
            AND (frompartner_id IS NULL OR frompartner_id=%(frompartner)s OR frompartner_id in (
                SELECT to_partner_id
                FROM partnergroup
                WHERE from_partner_id=%(frompartner)s ))
            AND (topartner_id IS NULL OR topartner_id=%(topartner)s OR topartner_id in (
                SELECT to_partner_id
                FROM partnergroup
                WHERE from_partner_id=%(topartner)s ))
            ORDER BY alt DESC,
                     CASE WHEN frompartner_id IS NULL THEN 1 ELSE 0 END, frompartner_id ,
                     CASE WHEN topartner_id IS NULL THEN 1 ELSE 0 END, topartner_id """,
        {
            'frommessagetype': frommessagetype,
            'fromeditype': fromeditype,
            'alt': alt,
            'frompartner': frompartner,
            'topartner': topartner,
            'booll': True,
        },
    ):
        return row["tscript"], row["toeditype"], row["tomessagetype"]
    return None, None, None


def prepare_confirmrules():
    """
    Read confirmrules into memory for efficient repeated access.
    """
    for confirmdict in query(
        """SELECT confirmtype,
            ruletype,
            idroute,
            idchannel_id as idchannel,
            frompartner_id as frompartner,
            topartner_id as topartner,
            messagetype,negativerule
        FROM confirmrule
        WHERE active=%(active)s
        ORDER BY negativerule ASC
        """,
        {'active': True},
    ):
        state.confirmrules.append(dict(confirmdict))


def set_asked_confirmrules(routedict, rootidta):
    """Set ask-confirmation flags for x12 and edifact output transactions."""
    if not globalcheckconfirmrules('ask-x12-997') \
            and not globalcheckconfirmrules('ask-edifact-CONTRL'):
        return
    for row in query(
        """SELECT parent,editype,messagetype,frompartner,topartner
           FROM ta
           WHERE idta>%(rootidta)s
           AND status=%(status)s
           AND statust=%(statust)s
           AND (editype='edifact' OR editype='x12') """,
        {'status': FILEOUT, 'statust': OK, 'rootidta': rootidta},
    ):
        if row["editype"] == "x12":
            if row["messagetype"][:3] in ["997", "999"]:
                continue
            confirmtype = 'ask-x12-997'
        else:
            if row["messagetype"][:6] in ["CONTRL", "APERAK"]:
                continue
            confirmtype = 'ask-edifact-CONTRL'
        if not checkconfirmrules(
                confirmtype,
                idroute=routedict['idroute'],
                idchannel=routedict['tochannel'],
                topartner=row["topartner"],
                frompartner=row["frompartner"],
                messagetype=row["messagetype"]):
            continue
        changeq(
            """UPDATE ta
                   SET confirmasked=%(confirmasked)s, confirmtype=%(confirmtype)s
                   WHERE idta=%(parent)s """,
            {"parent": row["parent"], "confirmasked": True, "confirmtype": confirmtype},
        )
