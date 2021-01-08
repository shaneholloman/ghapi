# AUTOGENERATED! DO NOT EDIT! File to edit: 03_page.ipynb (unless otherwise specified).

__all__ = ['paged', 'parse_link_hdr', 'pages']

# Cell
from fastcore.utils import *
from fastcore.foundation import *
from .core import *

import re
from urllib.parse import parse_qs,urlsplit

# Cell
def paged(oper, *args, per_page=30, max_pages=9999, **kwargs):
    "Convert operation `oper(*args,**kwargs)` into an iterator"
    yield from itertools.takewhile(noop, (oper(*args, per_page=per_page, page=i, **kwargs) for i in range(1,max_pages+1)))

# Cell
class _Scanner:
    def __init__(self, buf): self.buf,self.match = buf,None
    def __getitem__(self, key): return self.match.group(key)
    def scan(self, pattern):
        self.match = re.compile(pattern).match(self.buf)
        if self.match: self.buf = self.buf[self.match.end():]
        return self.match

_QUOTED        = r'"((?:[^"\\]|\\.)*)"'
_TOKEN         = r'([^()<>@,;:\"\[\]?={}\s]+)'
_RE_COMMA_HREF = r' *,? *< *([^>]*) *> *'
_RE_ATTR       = rf'{_TOKEN} *(?:= *({_TOKEN}|{_QUOTED}))? *'

# Cell
def _parse_link_hdr(header):
    "Parse an RFC 5988 link header, returning a `list` of `tuple`s of URL and attr `dict`"
    scanner,links = _Scanner(header),[]
    while scanner.scan(_RE_COMMA_HREF):
        href,attrs = scanner[1],[]
        while scanner.scan('; *'):
            if scanner.scan(_RE_ATTR):
                attr_name, token, quoted = scanner[1], scanner[3], scanner[4]
                if quoted is not None: attrs.append([attr_name, quoted.replace(r'\"', '"')])
                elif token is not None: attrs.append([attr_name, token])
                else: attrs.append([attr_name, None])
        links.append((href,dict(attrs)))
    if scanner.buf: raise Exception(f"parse() failed at {scanner.buf!r}")
    return links

# Cell
def parse_link_hdr(header):
    "Parse an RFC 5988 link header, returning a `dict` from rels to a `tuple` of URL and attrs `dict`"
    return {a.pop('rel'):(u,a) for u,a in _parse_link_hdr(header)}

# Cell
@patch
def last_page(self:GhApi):
    "Parse RFC 5988 link header from most recent operation, and extract the last page"
    header = self.recv_hdrs.get('Link', '')
    last = nested_idx(parse_link_hdr(header), 'last', 0) or ''
    qs = parse_qs(urlsplit(last).query)
    return int(nested_idx(qs,'page',0) or 0)

# Cell
def _call_page(i, oper, args, kwargs, per_page):
    return oper(*args, per_page=per_page, page=i, **kwargs)

# Cell
def pages(oper, n_pages, *args, n_workers=None, per_page=100, **kwargs):
    "Get `n_pages` pages from `oper(*args,**kwargs)`"
    return parallel(_call_page, range(1,n_pages+1), oper=oper, per_page=per_page, args=args, kwargs=kwargs,
                    progress=False, n_workers=ifnone(n_workers,n_pages), threadpool=True)