from __future__ import annotations
import json
from typing import TYPE_CHECKING, Any, Sequence
from argparse import (
    Namespace,
    _HelpAction,
    _StoreAction,
    _StoreConstAction,
    _AppendAction,
    _AppendConstAction,
    _CountAction,
    _SubParsersAction,
    # Introduced in python3.9
    # _ExtendAction,
)

from .utils import get_ns_dest, copy_items, add_attribute

if TYPE_CHECKING:
    from .parser import ArgumentParser


@add_attribute("show", True)
class StoreAction(_StoreAction):
    def __call__(  # type: ignore[override]
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        ns, dest = get_ns_dest(namespace, self.dest)
        setattr(ns, dest, values)


@add_attribute("show", True)
class StoreConstAction(_StoreConstAction):
    def __call__(  # type: ignore[override]
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        ns, dest = get_ns_dest(namespace, self.dest)
        setattr(ns, dest, self.const)


class StoreTrueAction(StoreConstAction):
    def __init__(self, *args, **kwargs):
        kwargs["const"] = True
        super().__init__(*args, **kwargs)


class StoreFalseAction(StoreConstAction):
    def __init__(self, *args, **kwargs):
        kwargs["const"] = False
        super().__init__(*args, **kwargs)


@add_attribute("show", True)
class AppendAction(_AppendAction):
    def __call__(  # type: ignore[override]
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        ns, dest = get_ns_dest(namespace, self.dest)
        items = getattr(ns, dest, None)
        items = copy_items(items)
        items.append(values)
        setattr(ns, dest, items)


@add_attribute("show", True)
class AppendConstAction(_AppendConstAction):
    def __call__(  # type: ignore[override]
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        ns, dest = get_ns_dest(namespace, self.dest)
        items = getattr(ns, dest, None)
        items = copy_items(items)
        items.append(self.const)
        setattr(ns, dest, items)


@add_attribute("show", True)
class CountAction(_CountAction):
    def __call__(  # type: ignore[override]
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        ns, dest = get_ns_dest(namespace, self.dest)
        value = getattr(ns, dest, None)
        if value is None:
            value = 0
        setattr(ns, dest, value + 1)


class ExtendAction(AppendAction):
    def __call__(  # type: ignore[override]
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        ns, dest = get_ns_dest(namespace, self.dest)
        items = getattr(ns, dest, None)
        items = copy_items(items)
        items.extend(values)
        setattr(ns, dest, items)


class ClearAppendAction(AppendAction):
    """Append a list of values to the list of values for a given option"""

    def __init__(self, *args, **kwargs):
        self.received = False
        super().__init__(*args, **kwargs)

    def __call__(  # type: ignore[override]
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        ns, dest = get_ns_dest(namespace, self.dest)
        if not self.received:
            items = []
            self.received = True
        else:
            items = getattr(ns, dest, None)
            items = copy_items(items)

        items.append(values)
        setattr(ns, dest, items)


class ClearExtendAction(ClearAppendAction):
    def __call__(  # type: ignore[override]
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        ns, dest = get_ns_dest(namespace, self.dest)
        if not self.received:
            items = []
            self.received = True
        else:
            items = getattr(ns, dest, None)
            items = copy_items(items)

        items.extend(values)
        setattr(ns, dest, items)


@add_attribute("show", True)
class NamespaceAction(_StoreAction):
    """Receive a json and parse and spread it to the namespace"""

    def __call__(  # type: ignore[override]
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        ns, dest = get_ns_dest(namespace, self.dest)
        if isinstance(values, str):
            try:
                parsed = json.loads(values)
            except json.JSONDecodeError:
                parser.error(f"Invalid json for {option_string}: {values}")

        if not isinstance(parsed, dict):
            parser.error(f"Invalid json dictionary for {option_string}: {values}")

        def _update_ns(nsc: Namespace, dct: dict[str, Any]) -> None:
            for key, value in dct.items():
                if not isinstance(value, dict):
                    setattr(nsc, key, value)
                else:
                    if getattr(nsc, key, None) is None:
                        setattr(nsc, key, Namespace())
                    _update_ns(getattr(nsc, key), value)

        _update_ns(ns, {dest: parsed})


class SubParserAction(_SubParsersAction):

    def add_parser(self, *args, **kwargs) -> ArgumentParser:
        parser = super().add_parser(*args, **kwargs)
        parser.parent = self.parent
        return parser


@add_attribute("show", True)
class HelpAction(_HelpAction):
    def __call__(  # type: ignore[override]
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        parser.print_help(
            # This is a + option
            plus=option_string.endswith("+")
            # Or no + option defined at all, all options are shown
            or not any(h.endswith("+") for h in parser.add_help)
        )
        parser.exit()
