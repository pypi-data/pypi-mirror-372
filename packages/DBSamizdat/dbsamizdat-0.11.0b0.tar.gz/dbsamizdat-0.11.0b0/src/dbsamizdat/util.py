from typing import Union
from re import compile as rexcompile
from math import log10, ceil

LEADING_WHITESPACE_REX = rexcompile(r'^(\s*).*$')
PGCursor2 = None
PGCursor3 = None

from psycopg import Cursor as PGCursor3  # noqa E402, F811
try:
    from psycopg2.extensions import cursor as PGCursor2
except ModuleNotFoundError:
    pass

CURSOR_TYPES = tuple(filter(None, (PGCursor2, PGCursor3)))

def fqify_node(node):
    """
    normalize node names to (schema, nodename) format, assuming the 'public' schema for not-fully-qualified node names
    """
    if isinstance(node, str):
        firstpart, *rest = node.split('.', maxsplit=1)
        if rest:
            return (firstpart, rest[0])
        return ("public", firstpart)
    return node


def nodenamefmt(node):
    """
    format node for presentation purposes. If it's in the public schema, omit the "public" for brevity.
    """
    if isinstance(node, str):
        return node
    if isinstance(node, tuple):
        schema, name, *args = node
        identifier = f"{schema}.{name}" if schema not in {'public', None} else name
        if args and args[0]:
            return f'{identifier}({args[0]})'
        return identifier
    return str(node)  # then it should be a Samizdat


def db_object_identity(thing):
    schema, name, *fnargs = fqify_node(thing)
    args = f'({fnargs[0]})' if fnargs else ''
    return '"%s"."%s"%s' % (schema, name, args)


def sqlfmt(text: str, indent_with='', number_lines=False):
    """
    Tidy up chaotically indented text by stripping the common whitespace prefixes
    and replacing all-whitespace lines with empty lines.
    """
    # strip leading and trailing whitespace lines
    wstagged = [(l.strip() == '', l.rstrip()) for l in text.splitlines()]
    def nonws_slice():
        wsmap = [isws for isws,_ in wstagged]
        def nonws_index(the_map):
            try:
                return the_map.index(False)
            except ValueError:
                return 0
        return slice(
            nonws_index(wsmap),
            -nonws_index(wsmap[::-1]) or None
        )
    tagged_as_wsline = wstagged[nonws_slice()]
    unique_ws_prefixes = sorted(set((m.groups()[0] if (m := LEADING_WHITESPACE_REX.match(l)) else '') for isws, l in tagged_as_wsline if not isws), key=len)
    common_leading_ws_chars_no = 0
    if unique_ws_prefixes:
        for i in range(len(unique_ws_prefixes[0])):
            if len({p[i] for p in unique_ws_prefixes}) == 1:
                common_leading_ws_chars_no += 1
            else:
                break
    lineno_fmtstring  = '{: <%d}:' % ceil(log10(len(tagged_as_wsline) or 1))
    def fmt_lineno(no: int):
        if not number_lines:
            return ''
        return lineno_fmtstring.format(no)
    fmted = [fmt_lineno(lineno) + ('' if isws else indent_with + l[common_leading_ws_chars_no:]) for lineno, (isws, l) in enumerate(tagged_as_wsline, 1)]
    return '\n'.join(fmted) + '\n'


def honest_cursor(cursor) -> Union[PGCursor2, PGCursor3]:
    """
    Sometimes you need the real PsycoPG cursor instead of proxy objects (Django cursor, or a DebugCursor underneath, ...)
    This will try to dig down to the real cursor, returning it.
    """
    if isinstance(cursor, CURSOR_TYPES):
        return cursor
    try:
        return honest_cursor(cursor.cursor)
    except AttributeError:
        raise ValueError("Quest for an actual PsycoPG cursor was unfruitful :-/")
