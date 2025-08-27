# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Enum utilities with support for deprecated members.

This module provides an [`Enum`][frequenz.core.enum.Enum] base class that extends the
standard library's [`enum.Enum`][] to support marking certain members as deprecated.

See the [class documentation][frequenz.core.enum.Enum] for details and examples.
"""

from __future__ import annotations

import enum
import warnings
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, ClassVar, Self, TypeVar, cast

# Note: This module contains more casts and uses of Any than what's typically
# ideal. This is because type hinting EnumType and Enum subclasses is quite
# challenging, as there is a lot of special behavior in `mypy` for these classes.
#
# The resulting enum should be treated as a regular enum by mypy, so hopefully everthing
# still works as expected.

EnumT = TypeVar("EnumT", bound=enum.Enum)
"""Type variable for enum types."""


class DeprecatedMemberWarning(DeprecationWarning):
    """Warning category for deprecated enum members."""


class DeprecatedMember:
    """Marker used in enum class bodies to declare deprecated members.

    Please read the [`Enum`][frequenz.core.enum.Enum] documentation for details and
    examples.
    """

    # Using slots is just an optimization to make the class more lightweight and avoid
    # the creation of a `__dict__` for each instance and its corresponding lookup.
    __slots__ = ("value", "message")

    def __init__(self, value: Any, message: str) -> None:
        """Initialize this instance."""
        self.value = value
        self.message = message


class DeprecatingEnumType(enum.EnumType):
    """Enum metaclass that supports `DeprecatedMember` wrappers.

    Tip:
        Normally it is not necessary to use this class directly, use
        [`Enum`][frequenz.core.enum.Enum] instead.

    Behavior:

    - In the class body, members may be declared as `NAME = DeprecatedMember(value, msg)`.
    - During class creation, these wrappers are replaced with `value` so that
      a normal enum member or alias is created by [`EnumType`][enum.EnumType].
    - The deprecated names are recorded so that:

        * `MyEnum.NAME` warns (attribute access by name)
        * `MyEnum["NAME"]` warns (lookup by name)
        * `MyEnum(value)` warns **only if** the resolved member has **no**
            non-deprecated aliases (all names for that member are deprecated).
    """

    def __new__(  # pylint: disable=too-many-locals
        mcs,
        name: str,
        bases: tuple[type[EnumT], ...],
        classdict: Mapping[str, Any],
        **kw: Any,
    ) -> type[EnumT]:
        """Create the new enum class, rewriting `DeprecatedMember` instances."""
        deprecated_names: dict[str, str] = {}
        prepared = super().__prepare__(name, bases, **kw)

        # Unwrap DeprecatedMembers and record them as deprecated
        for key, value in classdict.items():
            if isinstance(value, DeprecatedMember):
                deprecated_names[key] = value.message
                prepared[key] = value.value
            else:
                prepared[key] = value

        cls = cast(type[EnumT], super().__new__(mcs, name, bases, prepared, **kw))

        # Build alias groups: member -> list of names
        member_to_names: dict[EnumT, list[str]] = {}
        member: EnumT
        for member_name, member in cls.__members__.items():
            member_to_names.setdefault(member, []).append(member_name)

        warned_by_member: dict[EnumT, str] = {}
        for member, names in member_to_names.items():
            # warn on value only if all alias names are deprecated
            deprecated_aliases = [n for n in names if n in deprecated_names]
            if deprecated_aliases and len(deprecated_aliases) == len(names):
                warned_by_member[member] = deprecated_names[deprecated_aliases[0]]

        # Inject maps quietly
        type.__setattr__(cls, "__deprecated_names__", deprecated_names)
        type.__setattr__(cls, "__deprecated_value_map__", warned_by_member)

        return cls

    @staticmethod
    def _name_map(cls_: type[Any]) -> Mapping[str, str]:
        """Map from member names to deprecation messages."""
        return cast(
            Mapping[str, str],
            type.__getattribute__(cls_, "__dict__").get("__deprecated_names__", {}),
        )

    @staticmethod
    def _value_map(cls_: type[Any]) -> Mapping[Any, str]:
        """Map from enum members to deprecation messages."""
        return cast(
            Mapping[Any, str],
            type.__getattribute__(cls_, "__dict__").get("__deprecated_value_map__", {}),
        )

    def __getattribute__(cls, name: str) -> Any:
        """Resolve `name` to a member, warning if the member is deprecated."""
        if name in ("__deprecated_names__", "__deprecated_value_map__"):
            return type.__getattribute__(cls, name)
        deprecated = DeprecatingEnumType._name_map(cls)
        if name in deprecated:
            warnings.warn(deprecated[name], DeprecatedMemberWarning, stacklevel=2)
        return super().__getattribute__(name)

    def __getitem__(cls, name: str) -> Any:
        """Resolve `name` to a member, warning if the member is deprecated."""
        deprecated = DeprecatingEnumType._name_map(cls)
        if name in deprecated:
            warnings.warn(deprecated[name], DeprecatedMemberWarning, stacklevel=2)
        return super().__getitem__(name)

    def __call__(cls, value: Any, *args: Any, **kwargs: Any) -> Any:
        """Resolve `value` to a member, warning if the member is purely deprecated."""
        member = super().__call__(value, *args, **kwargs)
        value_map: Mapping[Any, str] = DeprecatingEnumType._value_map(cls)
        msg = value_map.get(member)
        if msg is not None:
            warnings.warn(msg, DeprecatedMemberWarning, stacklevel=2)
        return member


if TYPE_CHECKING:
    # Make type checkers treat it as a plain Enum (so member checks work), if we don't
    # do this, mypy will consider the resulting enum completely dynamic and never
    # complain if an unexisting member is accessed.

    # pylint: disable-next=missing-class-docstring
    class Enum(enum.Enum):  # noqa
        __deprecated_names__: ClassVar[Mapping[str, str]]
        __deprecated_value_map__: ClassVar[Mapping[Enum, str]]

else:

    class Enum(enum.Enum, metaclass=DeprecatingEnumType):
        """Base class for enums that support DeprecatedMember.

        This class extends the standard library's [`enum.Enum`][] to support marking
        certain members as deprecated. Deprecated members can be accessed, but doing so
        will emit a [`DeprecationWarning`][], specifically
        a [`DeprecatedMemberWarning`][frequenz.core.enum.DeprecatedMemberWarning].

        To declare a deprecated member, use the
        [`DeprecatedMember`][frequenz.core.enum.DeprecatedMember] wrapper in the class body.

        When using the enum constructor (i.e. `MyEnum(value)`), a warning is only emitted if
        the resolved member has no non-deprecated aliases. If there is at least one
        non-deprecated alias for the member, no warning is emitted.

        Example:
            ```python
            from frequenz.core.enum import Enum, DeprecatedMember

            class TaskStatus(Enum):
                OPEN = 1
                IN_PROGRESS = 2
                PENDING = DeprecatedMember(1, "PENDING is deprecated, use OPEN instead")
                DONE = DeprecatedMember(3, "DONE is deprecated, use FINISHED instead")
                FINISHED = 4

            # Accessing deprecated members:
            status1 = TaskStatus.PENDING  # Warns: "PENDING is deprecated, use OPEN instead"
            assert status1 is TaskStatus.OPEN

            status2 = TaskStatus["DONE"]  # Warns: "DONE is deprecated, use FINISHED instead"
            assert status2 is TaskStatus.FINISHED

            status3 = TaskStatus(1)  # No warning, resolves to OPEN which has a non-deprecated alias
            assert status3 is TaskStatus.OPEN

            status4 = TaskStatus(3)  # Warns: "DONE is deprecated, use FINISHED instead"
            assert status4 is TaskStatus.FINISHED
            ```
        """

        __deprecated_names__: ClassVar[Mapping[str, str]]
        __deprecated_value_map__: ClassVar[Mapping[Self, str]]
