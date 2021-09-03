from dataclasses import asdict
from os.path import normcase
from pathlib import Path
from typing import AbstractSet, Iterable, Iterator, MutableMapping, MutableSet, Sequence
from uuid import UUID, uuid3

from std2.locale import pathsort_key
from std2.pathlib import walk
from std2.tree import recur_sort

from ..types import LoadedSnips, ParsedSnippet
from .lsp import parse as parse_lsp
from .neosnippet import parse as parse_neosnippets
from .ultisnip import parse as parse_ultisnip


def _load_paths(search: Iterable[Path], exts: AbstractSet[str]) -> Sequence[Path]:
    def cont() -> Iterator[Path]:
        for search_path in search:
            for path in walk(search_path):
                if path.suffix in exts:
                    yield Path(normcase(path))

    return sorted(cont(), key=pathsort_key)


def _key(snip: ParsedSnippet) -> UUID:
    name = str(recur_sort(asdict(snip)))
    return uuid3(UUID(int=0), name=name)


def load(
    lsp: Iterable[Path],
    neosnippet: Iterable[Path],
    ultisnip: Iterable[Path],
) -> LoadedSnips:
    specs = {
        parse_lsp: _load_paths(lsp, exts={".json"}),
        parse_neosnippets: _load_paths(neosnippet, exts={".snippets", ".snip"}),
        parse_ultisnip: _load_paths(ultisnip, exts={".snippets", ".snip"}),
    }

    extensions: MutableMapping[str, MutableSet[str]] = {}
    snippets: MutableMapping[UUID, ParsedSnippet] = {}

    for parser, paths in specs.items():
        for path in paths:
            with path.open(encoding="UTF-8") as fd:
                filetype, exts, snips = parser(path, enumerate(fd, start=1))
                ext_acc = extensions.setdefault(filetype, set())
                for ext in exts:
                    ext_acc.add(ext)
                for snip in snips:
                    uid = _key(snip)
                    snippets[uid] = snip

    loaded = LoadedSnips(exts=extensions, snippets=snippets)
    return loaded
