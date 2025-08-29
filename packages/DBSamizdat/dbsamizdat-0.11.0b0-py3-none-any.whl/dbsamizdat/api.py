"""
API for using dbsamizdat as a library
"""

from argparse import Namespace as _Namespace
from typing import Iterable, Union

from .runner import cmd_refresh as _cmd_refresh, cmd_sync as _cmd_sync, cmd_nuke as _cmd_nuke
from .const import txstyle, env
from .samizdat import Samizdat
from .exceptions import WrongTransactionStyleForParallelRefresh

_CMD_ARG_DEFAULTS = dict(
    context=env.API,
    verbosity=1,
    parallel=False,
)


def refresh(dburl: str, samizdatmodules: Iterable[str], transaction_style: txstyle = txstyle.CHECKPOINT, belownodes: Iterable[Union[str, tuple, Samizdat]] = tuple(), parallel: bool = False):
    """
    Refresh materialized views, in dependency order, optionally parallelized (where the dependency tree allows), optionally restricted to views depending directly or transitively on any of the DB objects specified in `belownodes`.
    """
    if parallel and transaction_style != txstyle.CHECKPOINT:
        raise WrongTransactionStyleForParallelRefresh()
    args = _Namespace(
        **_CMD_ARG_DEFAULTS,
        dburl=dburl,
        samizdatmodules=[(None, m) for m in samizdatmodules],
        txdiscipline=transaction_style.value,
        belownodes=belownodes,
        parallel=parallel,
    )
    _cmd_refresh(args)


def sync(dburl: str, samizdatmodules: Iterable[str], transaction_style: txstyle = txstyle.JUMBO, parallel=False):
    """
    Sync dbsamizdat state to the DB.
    """
    if parallel and transaction_style != txstyle.CHECKPOINT:
        raise WrongTransactionStyleForParallelRefresh()
    args = _Namespace(
        **_CMD_ARG_DEFAULTS,
        dburl=dburl,
        samizdatmodules=[(None, m) for m in samizdatmodules],
        txdiscipline=transaction_style.value,
        parallel=parallel,
    )
    _cmd_sync(args)


def nuke(dburl: str, transaction_style: txstyle = txstyle.JUMBO):
    """Remove any database object tagged as samizdat."""
    args = _Namespace(
        **_CMD_ARG_DEFAULTS,
        dburl=dburl,
        txdiscipline=transaction_style.value,
    )
    _cmd_nuke(args)
