from datetime import datetime
from typing import Generic, Optional, Sequence, TypeVar

from confflow.types import Value

from ..constraints import (
    AllItemsMatch,
    Constraint,
    EnumValues,
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
    MaxItems,
    MaxLength,
    MinItems,
    MinLength,
    Regex,
    UniqueItems,
)

T = TypeVar("T", bound=Value, covariant=True)


class Field(Generic[T]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: Optional[T] = None,
        constraints: Optional[Sequence[Constraint[T]]] = None,
    ):
        self._name: str = name
        self._description: str = description

        if constraints and len(constraints) != len(set(type(c) for c in constraints)):
            raise ValueError("Cannot have multiple constraints of the same type")

        self._constraints: frozenset[Constraint[T]] = (
            frozenset(constraints) if constraints else frozenset()
        )
        self._default_value = (
            self._validate(default_value)
            if default_value is not None
            else default_value
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def default_value(self) -> Optional[T]:
        return self._default_value

    @property
    def constraints(self) -> frozenset[Constraint[T]]:
        return self._constraints

    def _validate(self, value: T) -> T:  # type: ignore
        for constraint in self._constraints:
            constraint(value)

        return value

    def __repr__(self) -> str:
        return (
            f"Field(name={self.name!r}, "
            f"default={self.default_value!r}, "
            f"constraints={len(self.constraints)})"
        )


## BASIC FIELDS
class StringField(Field[str]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: Optional[str] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        enum: Optional[list[str]] = None,
    ):
        constraints: list[Constraint[str]] = []
        if min_length:
            constraints.append(MinLength(min_length))
        if max_length:
            constraints.append(MaxLength(max_length))
        if regex:
            constraints.append(Regex(regex))
        if enum:
            constraints.append(EnumValues(enum))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class StringListField(Field[list[str]]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: Optional[list[str]] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_items: Optional[bool] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        enum: Optional[list[str]] = None,
    ):
        constraints: list[Constraint[list[str]]] = []

        if min_items:
            constraints.append(MinItems(min_items))
        if max_items:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        item_constraints: list[Constraint[str]] = []

        if min_length:
            item_constraints.append(MinLength(min_length))
        if max_length:
            item_constraints.append(MaxLength(max_length))
        if regex:
            item_constraints.append(Regex(regex))
        if enum:
            item_constraints.append(EnumValues(enum))

        if item_constraints:
            constraints.append(AllItemsMatch[list[str]](*item_constraints))  # type: ignore

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class IntegerField(Field[int]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: Optional[int] = None,
        gt: Optional[int] = None,
        ge: Optional[int] = None,
        lt: Optional[int] = None,
        le: Optional[int] = None,
    ):
        constraints: list[Constraint[int]] = []

        if gt:
            constraints.append(GreaterThan(gt))
        if ge:
            constraints.append(GreaterThanOrEqual(ge))
        if lt:
            constraints.append(LessThan(lt))
        if le:
            constraints.append(LessThanOrEqual(le))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class IntegerListField(Field[list[int]]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: Optional[list[int]] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_items: Optional[bool] = None,
        gt: Optional[int] = None,
        ge: Optional[int] = None,
        lt: Optional[int] = None,
        le: Optional[int] = None,
    ):
        constraints: list[Constraint[list[int]]] = []

        if min_items:
            constraints.append(MinItems(min_items))
        if max_items:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        item_constraints: list[Constraint[int]] = []

        if gt:
            item_constraints.append(GreaterThan(gt))
        if ge:
            item_constraints.append(GreaterThanOrEqual(ge))
        if lt:
            item_constraints.append(LessThan(lt))
        if le:
            item_constraints.append(LessThanOrEqual(le))

        if item_constraints:
            constraints.append(
                AllItemsMatch[list[int]](*item_constraints)  # type: ignore
            )

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class FloatField(Field[float]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: Optional[float] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
    ):
        constraints: list[Constraint[float]] = []

        if gt:
            constraints.append(GreaterThan(gt))
        if ge:
            constraints.append(GreaterThanOrEqual(ge))
        if lt:
            constraints.append(LessThan(lt))
        if le:
            constraints.append(LessThanOrEqual(le))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class FloatListField(Field[list[float]]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: Optional[list[float]] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_items: Optional[bool] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
    ):
        constraints: list[Constraint[list[float]]] = []

        if min_items:
            constraints.append(MinItems(min_items))
        if max_items:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        item_constraints: list[Constraint[float]] = []

        if gt:
            item_constraints.append(GreaterThan(gt))
        if ge:
            item_constraints.append(GreaterThanOrEqual(ge))
        if lt:
            item_constraints.append(LessThan(lt))
        if le:
            item_constraints.append(LessThanOrEqual(le))

        if item_constraints:
            constraints.append(
                AllItemsMatch[list[float]](*item_constraints)  # type: ignore
            )

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class DateField(Field[datetime]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: Optional[datetime] = None,
    ):
        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=[],
        )


class DateListField(Field[list[datetime]]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: Optional[list[datetime]] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_items: Optional[bool] = None,
    ):
        constraints: list[Constraint[list[datetime]]] = []

        if min_items:
            constraints.append(MinItems(min_items))
        if max_items:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class BytesField(Field[bytes]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: Optional[bytes] = None,
    ):
        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=[],
        )


class BooleanListField(Field[list[bool]]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: Optional[list[bool]] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_items: Optional[bool] = None,
    ):
        constraints: list[Constraint[list[bool]]] = []

        if min_items:
            constraints.append(MinItems(min_items))
        if max_items:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class BooleanField(Field[bool]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: Optional[bool] = None,
    ):
        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=[],
        )


class BytesListField(Field[list[bytes]]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: Optional[list[bytes]] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_items: Optional[bool] = None,
    ):
        constraints: list[Constraint[list[bytes]]] = []

        if min_items:
            constraints.append(MinItems(min_items))
        if max_items:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )
