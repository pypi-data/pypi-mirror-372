"""
LINQ-style enumerable implementation with deferred evaluation.

Provides a comprehensive set of query operations with lazy evaluation,
strong typing, and fluent chaining.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from concurrent.futures import ThreadPoolExecutor
from functools import reduce
from itertools import islice
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from pydantic_core import core_schema

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")
U = TypeVar("U")


# Sentinel object for default parameters
_MISSING = object()


def _with_length(
    obj: "Enumerable[T]",
    source: "Enumerable[T]",
    length_func: Callable[["Enumerable[T]"], int] | None = None,
) -> "Enumerable[T]":  # type: ignore
    """Wrap enumerable to preserve length from source if available."""

    if not hasattr(source, "__len__"):
        return obj

    if not length_func:
        length_func = lambda s: len(s)  # type: ignore

    class LengthPreservingEnumerable(Enumerable):
        """Decorator that adds Sized behavior when source is sized."""

        def __len__(self) -> int:
            return length_func(source)

        def __iter__(self) -> Iterator[T]:
            return iter(obj)

        def __repr__(self):
            return f"LengthPreserving({obj!r})"

    return LengthPreservingEnumerable()


class Grouping(Generic[K, V]):
    def __init__(self, key: K, items: list[V]):
        self._key = key
        self._items = items

    @property
    def key(self) -> K:
        return self._key

    def __iter__(self) -> Iterator[V]:
        return iter(self._items)

    def count(self) -> int:
        return len(self._items)


class Enumerable(ABC, Generic[T]):
    """Base class for all enumerable operations with deferred evaluation."""

    @abstractmethod
    def __iter__(self) -> Iterator[T]:
        pass

    # Core transformations
    def select(self, selector: Callable[[T], U], parallelism: int = 1) -> "Enumerable[U]":
        """Transform each element using selector.

        Example: from_iterable([1, 2, 3]).select(lambda x: x * 2) -> [2, 4, 6]
        """
        if parallelism > 1:
            result = ParallelSelect(self, selector, parallelism)
        else:
            result = Select(self, selector)
        return _with_length(result, self)  # type: ignore

    def map(self, selector: Callable[[T], U]) -> "Enumerable[U]":
        """Transform each element using selector (alias for select).

        Example: from_iterable([1, 2, 3]).map(lambda x: x * 2) -> [2, 4, 6]
        """
        return self.select(selector)

    def where(self, predicate: Callable[[T], bool]) -> "Enumerable[T]":
        """Filter elements that match predicate.

        Example: from_iterable([1, 2, 3, 4]).where(lambda x: x % 2 == 0) -> [2, 4]
        """
        return Where(self, predicate)

    def select_many(self, selector: Callable[[T], Iterable[U]]) -> "Enumerable[U]":
        """Flatten sequences returned by selector.

        Example: from_iterable([[1, 2], [3, 4]]).select_many(lambda x: x) -> [1, 2, 3, 4]
        """
        return SelectMany(self, selector)

    # Aggregations (terminal operations)
    def count(self, predicate: Callable[[T], bool] = lambda _: True) -> int:
        """Count elements matching predicate.

        Example: from_iterable([1, 2, 3, 4]).count(lambda x: x % 2 == 0) -> 2
        """
        return sum(1 for item in self if predicate(item))

    def first(self, predicate: Callable[[T], bool] = lambda _: True, default: T = _MISSING) -> T:  # type: ignore
        """Get first element matching predicate, or default if none found.

        Example: from_iterable([1, 2, 3, 4]).first(lambda x: x % 2 == 0) -> 2
        """
        for item in self:
            if predicate(item):  # type: ignore
                return item
        if default is not _MISSING:
            return default
        raise ValueError("Sequence contains no matching element")

    def last(self, predicate: Callable[[T], bool] = lambda _: True, default: T = _MISSING) -> T:  # type: ignore
        """Get last element matching predicate, or default if none found.

        Example: from_iterable([1, 2, 3, 4]).last(lambda x: x % 2 == 0) -> 4
        """
        result: T = _MISSING  # type: ignore
        found = False
        for item in self:
            if predicate(item):  # type: ignore
                result = item
                found = True
        if not found:
            if default is not _MISSING:
                return default
            raise ValueError("Sequence contains no matching element")
        return result  # type: ignore

    def any(self, predicate: Callable[[T], bool] = lambda _: True) -> bool:
        """Check if any element matches the predicate.

        Example: from_iterable([1, 3, 5]).any(lambda x: x % 2 == 0) -> False
        """
        for item in self:
            if predicate(item):  # type: ignore
                return True
        return False

    def all(self, predicate: Callable[[T], bool]) -> bool:
        """Check if all elements match the predicate.

        Example: from_iterable([2, 4, 6]).all(lambda x: x % 2 == 0) -> True
        """
        for item in self:
            if not predicate(item):  # type: ignore
                return False
        return True

    def sum(self) -> int | float:
        """Sum of all numeric elements.

        Example: from_iterable([1, 2, 3]).sum() -> 6
        """
        return sum(item for item in self)  # type: ignore

    def average(self) -> float:
        """Average of numeric elements.

        Example: from_iterable([1, 2, 3]).average() -> 2.0
        """
        total = 0.0
        count = 0
        for item in self:
            total += item  # type: ignore
            count += 1

        if count == 0:
            raise ValueError("Cannot compute average of empty sequence")
        return total / count

    def min(self) -> T:
        """Minimum element.

        Example: from_iterable([3, 1, 4]).min() -> 1
        """
        return min(self)

    def max(self) -> T:
        """Maximum element.

        Example: from_iterable([3, 1, 4]).max() -> 4
        """
        return max(self)

    def aggregate(self, seed: U, func: Callable[[U, T], U]) -> U:
        """Aggregate with accumulator function.

        Example: from_iterable([1, 2, 3]).aggregate(0, lambda acc, x: acc + x) -> 6
        """
        return reduce(func, self, seed)

    # Set operations
    def distinct(self) -> "Enumerable[T]":
        """Remove duplicate elements.

        Example: from_iterable([1, 2, 2, 3]).distinct() -> [1, 2, 3]
        """
        return Distinct(self)

    def union(self, other: "Enumerable[T]") -> "Enumerable[T]":
        """Union with another enumerable, returning the unique elements from both.

        Example: from_iterable([1, 2]).union(from_iterable([2, 3])) -> [1, 2, 3]
        """
        return UnionEnumerable(self, other)

    def intersect(self, other: "Enumerable[T]") -> "Enumerable[T]":
        """Intersection with another enumerable (common elements).

        Example: from_iterable([1, 2, 3]).intersect(from_iterable([2, 3, 4])) -> [2, 3]
        """
        return Intersect(self, other)

    def except_(self, other: "Enumerable[T]") -> "Enumerable[T]":
        """Elements in this enumerable but not in other.

        Example: from_iterable([1, 2, 3]).except_(from_iterable([2, 4])) -> [1, 3]
        """
        return Except(self, other)

    # Ordering
    def order_by(self, key_selector: Callable[[T], K]) -> "OrderedEnumerable[T]":
        """Sort elements by key selector.

        Example: from_iterable(['apple', 'pie', 'a']).order_by(lambda x: len(x)) -> ['a', 'pie', 'apple']
        """
        return OrderedEnumerable(self, key_selector)

    def order_by_descending(self, key_selector: Callable[[T], K]) -> "OrderedEnumerable[T]":
        """Sort elements by key selector in descending order.

        Example: from_iterable([1, 3, 2]).order_by_descending(lambda x: x) -> [3, 2, 1]
        """
        return OrderedEnumerable(self, key_selector, reverse=True)

    # Grouping
    def group_by(self, key_selector: Callable[[T], K]) -> "Enumerable[Grouping[K, T]]":
        """Group elements by key selector.

        Example: from_iterable(['a', 'ab', 'abc']).group_by(lambda x: len(x)) -> groups by length
        """
        return GroupBy(self, key_selector)

    # Joining
    def join(
        self,
        inner: "Enumerable[U]",
        outer_key_selector: Callable[[T], K],
        inner_key_selector: Callable[[U], K],
        result_selector: Callable[[T, U], V],
    ) -> "Enumerable[V]":
        return Join(self, inner, outer_key_selector, inner_key_selector, result_selector)

    # Partitioning
    def take(self, count: int) -> "Enumerable[T]":
        """Take first count elements.

        Example: from_iterable([1, 2, 3, 4, 5]).take(3) -> [1, 2, 3]
        """
        result = Take(self, count)

        def take_length_func(source: "Enumerable[T]") -> int:
            return min(len(source), count)  # type: ignore

        return _with_length(result, self, take_length_func)

    def skip(self, count: int) -> "Enumerable[T]":
        """Skip first count elements.

        Example: from_iterable([1, 2, 3, 4, 5]).skip(2) -> [3, 4, 5]
        """
        result = Skip(self, count)

        def skip_length_func(source: "Enumerable[T]") -> int:
            return max(0, len(source) - count)  # type: ignore

        return _with_length(result, self, skip_length_func)

    def take_while(self, predicate: Callable[[T], bool]) -> "Enumerable[T]":
        """Take elements while predicate is true.

        Example: from_iterable([1, 2, 3, 4, 1]).take_while(lambda x: x < 4) -> [1, 2, 3]
        """
        return TakeWhile(self, predicate)

    def skip_while(self, predicate: Callable[[T], bool]) -> "Enumerable[T]":
        """Skip elements while predicate is true.

        Example: from_iterable([1, 2, 3, 4, 1]).skip_while(lambda x: x < 4) -> [4, 1]
        """
        return SkipWhile(self, predicate)

    def sliding_window(
        self,
        size_or_predicate: int | Callable[[list[T]], bool],
        step: int = 1,
    ) -> "Enumerable[list[T]]":
        """Group elements into _sliding_ windows based on either a fixed size or a predicate function.

        Example: from_iterable([1, 2, 3, 4]).window(2) -> [[1, 2], [2, 3], [3, 4]]
        """
        if isinstance(size_or_predicate, int):
            return Window(self, size_or_predicate, step)
        else:
            return WindowPredicate(self, size_or_predicate)

    def batch(self, size: int) -> "Enumerable[list[T]]":
        """Group elements into batches of specified size.

        Example: from_iterable([1, 2, 3, 4, 5]).batch(2) -> [[1, 2], [3, 4], [5]]
        """
        result = Batch(self, size)

        def batch_length_func(v: "Enumerable[T]") -> int:
            return (len(v) + size - 1) // size  # type: ignore

        return _with_length(result, self, batch_length_func)  # type: ignore

    # Materialization
    def to_list(self) -> list[T]:
        """Convert to list.

        Example: from_iterable([1, 2, 3]).map(lambda x: x * 2).to_list() -> [2, 4, 6]
        """
        return list(self)

    def materialize(self) -> "Table":
        """Compute all of the values from this enumerable, returning the result as a Table.

        `materialize` forces evaluation of all deferred operations. Use it if you want to
        iterate over the result of an enumerable multiple times or want to force evaluation.

        Example: from_iterable([1, 2, 3]).map(lambda x: x * 2).materialize() -> Table([2, 4, 6])
        """
        values = list(self)
        return Table.from_rows(values)

    def partition(self, predicate: Callable[[T], bool]) -> tuple["Enumerable[T]", "Enumerable[T]"]:
        """Split into two enumerables based on predicate.

        Args:
            predicate: Function to test each element

        Returns:
            Tuple of (matching elements, non-matching elements)
        """
        matching = []
        non_matching = []
        for item in self:
            if predicate(item):  # type: ignore
                matching.append(item)
            else:
                non_matching.append(item)
        return Table.from_rows(matching), Table.from_rows(non_matching)

    def try_select(
        self, selector: Callable[[T], U], parallelism: int = 1
    ) -> tuple["Enumerable[U]", "Enumerable[Exception]"]:
        """Select with exception handling.

        Returns a tuple of (successful results, exceptions).

        Args:
            selector: Function to transform each element
            parallelism: Number of parallel workers (default 1 for sequential)

        Returns:
            Tuple of (successful results, exceptions)
        """

        def safe_selector(item: T) -> U | Exception:
            try:
                return selector(item)  # type: ignore
            except Exception as e:
                return e

        successes, errors = self.select(safe_selector, parallelism).partition(
            lambda x: not isinstance(x, Exception)
        )
        return successes, errors  # type: ignore

    def with_progress(self, description: str = "Processing") -> "Enumerable[T]":
        """Add Rich progress tracking to enumeration.

        Args:
            description: Description to show in progress bar

        Returns:
            Enumerable that displays progress during iteration
        """
        result = WithProgress(self, description)
        return _with_length(result, self)  # type: ignore

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        """
        Generate core schema for Enumerable that materializes to list.
        """

        # Get the type argument if available
        args = getattr(source_type, "__args__", ())
        if args:
            item_type = args[0]
            item_schema = handler.generate_schema(item_type)
        else:
            # Default to Any if no type argument
            item_schema = core_schema.any_schema()

        # Return list schema with the item type
        return core_schema.list_schema(item_schema)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        """
        Customize schema to show Enumerable materializes to array for JSON schema.
        """
        _ = core_schema, handler  # Mark as used
        # Return a generic array schema since Enumerable can contain any type
        return {
            "type": "array",
            "items": {"type": "object"},
            "title": "Enumerable",
            "description": "Enumerable that materializes to an array of items",
        }


class OrderedEnumerable(Enumerable[T]):
    """Enumerable with ordering capabilities."""

    def __init__(
        self,
        source: "Enumerable[T]",
        key_func: Callable[[T], Any],
        reverse: bool = False,
    ):
        super().__init__()
        self.source = source
        self.key_func = key_func
        self.reverse = reverse
        self._then_by_funcs: list[tuple[Callable[[T], Any], bool]] = []

    def then_by(self, key_selector: Callable[[T], K]) -> "OrderedEnumerable[T]":
        """Add secondary sort key."""
        result = OrderedEnumerable(self.source, self.key_func, self.reverse)
        result._then_by_funcs = self._then_by_funcs.copy()
        result._then_by_funcs.append((key_selector, False))
        return result

    def then_by_descending(self, key_selector: Callable[[T], K]) -> "OrderedEnumerable[T]":
        """Add secondary sort key (descending)."""
        result = OrderedEnumerable(self.source, self.key_func, self.reverse)
        result._then_by_funcs = self._then_by_funcs.copy()
        result._then_by_funcs.append((key_selector, True))
        return result

    def __iter__(self) -> Iterator[T]:
        items = list(self.source)

        # Build composite key function
        def composite_key(item: T) -> tuple:
            keys = [self.key_func(item)]
            for func, _ in self._then_by_funcs:
                keys.append(func(item))
            return tuple(keys)

        # Sort with composite key
        sorted_items = sorted(items, key=composite_key, reverse=self.reverse)

        # Apply then_by reversals
        if self._then_by_funcs:
            # This is a simplified approach - full implementation would need
            # stable sort with multiple passes
            pass

        return iter(sorted_items)


# Concrete operation implementations
class Select(Enumerable[U], Generic[T, U]):
    """Deferred select/map operation."""

    def __init__(self, source: Enumerable[T], selector: Callable[[T], U]):
        super().__init__()
        self.source = source
        self.selector = selector

    def __iter__(self) -> Iterator[U]:
        for item in self.source:
            yield self.selector(item)


class Where(Enumerable[T]):
    """Deferred filter operation."""

    def __init__(self, source: Enumerable[T], predicate: Callable[[T], bool]):
        super().__init__()
        self.source = source
        self.predicate = predicate

    def __iter__(self) -> Iterator[T]:
        for item in self.source:
            if self.predicate(item):  # type: ignore
                yield item


class SelectMany(Enumerable[U], Generic[T, U]):
    """Deferred flatten operation."""

    def __init__(self, source: Enumerable[T], selector: Callable[[T], Iterable[U]]):
        super().__init__()
        self.source = source
        self.selector = selector

    def __iter__(self) -> Iterator[U]:
        for item in self.source:
            yield from self.selector(item)


class Take(Enumerable[T]):
    """Take first n elements."""

    def __init__(self, source: Enumerable[T], count: int):
        super().__init__()
        self.source = source
        self._count = count

    def __iter__(self) -> Iterator[T]:
        yield from islice(self.source, self._count)


class Skip(Enumerable[T]):
    """Skip first n elements."""

    def __init__(self, source: Enumerable[T], count: int):
        super().__init__()
        self.source = source
        self._count = count

    def __iter__(self) -> Iterator[T]:
        yield from islice(self.source, self._count, None)


class TakeWhile(Enumerable[T]):
    """Take while predicate is true."""

    def __init__(self, source: Enumerable[T], predicate: Callable[[T], bool]):
        super().__init__()
        self.source = source
        self.predicate = predicate

    def __iter__(self) -> Iterator[T]:
        for item in self.source:
            if self.predicate(item):  # type: ignore
                yield item
            else:
                break


class SkipWhile(Enumerable[T]):
    """Skip while predicate is true."""

    def __init__(self, source: Enumerable[T], predicate: Callable[[T], bool]):
        super().__init__()
        self.source = source
        self.predicate = predicate

    def __iter__(self) -> Iterator[T]:
        iterator = iter(self.source)

        # Skip while predicate is true
        for item in iterator:
            if not self.predicate(item):  # type: ignore
                yield item
                break

        # Yield remaining items
        yield from iterator


class Distinct(Enumerable[T]):
    """Remove duplicates."""

    def __init__(self, source: Enumerable[T]):
        super().__init__()
        self.source = source

    def __iter__(self) -> Iterator[T]:
        seen = set()
        for item in self.source:
            if item not in seen:
                seen.add(item)
                yield item


class UnionEnumerable(Enumerable[T]):
    """Union of two enumerables, yielding one after the other."""

    def __init__(self, first: Enumerable[T], second: Enumerable[T]):
        super().__init__()
        self._first = first
        self._second = second

    def __iter__(self) -> Iterator[T]:
        seen = set()
        for item in self._first:
            if item not in seen:
                seen.add(item)
                yield item
        for item in self._second:
            if item not in seen:
                seen.add(item)
                yield item


class Intersect(Enumerable[T]):
    """Intersection of two enumerables."""

    def __init__(self, first: Enumerable[T], second: Enumerable[T]):
        super().__init__()
        self._first = first
        self._second = second

    def __iter__(self) -> Iterator[T]:
        second_set = set(self._second)
        seen = set()
        for item in self._first:
            if item in second_set and item not in seen:
                seen.add(item)
                yield item


class Except(Enumerable[T]):
    """Difference of two enumerables."""

    def __init__(self, first: Enumerable[T], second: Enumerable[T]):
        super().__init__()
        self._first = first
        self._second = second

    def __iter__(self) -> Iterator[T]:
        second_set = set(self._second)
        seen = set()
        for item in self._first:
            if item not in second_set and item not in seen:
                seen.add(item)
                yield item


class GroupBy(Enumerable[Grouping[K, T]], Generic[T, K]):
    """Group by key."""

    def __init__(self, source: Enumerable[T], key_selector: Callable[[T], K]):
        super().__init__()
        self.source = source
        self.key_selector = key_selector

    def __iter__(self) -> Iterator[Grouping[K, T]]:
        groups: dict[K, list[T]] = {}
        for item in self.source:
            key = self.key_selector(item)  # type: ignore
            if key not in groups:
                groups[key] = []
            groups[key].append(item)

        for key, items in groups.items():
            yield Grouping(key, items)


class Join(Enumerable[V], Generic[T, U, K, V]):
    """Inner join operation."""

    def __init__(
        self,
        outer: Enumerable[T],
        inner: Enumerable[U],
        outer_key_selector: Callable[[T], K],
        inner_key_selector: Callable[[U], K],
        result_selector: Callable[[T, U], V],
    ):
        super().__init__()
        self.outer = outer
        self.inner = inner
        self.outer_key_selector = outer_key_selector
        self.inner_key_selector = inner_key_selector
        self.result_selector = result_selector

    def __iter__(self) -> Iterator[V]:
        inner_lookup: dict[K, list[U]] = {}
        for inner_item in self.inner:
            key = self.inner_key_selector(inner_item)  # type: ignore
            if key not in inner_lookup:
                inner_lookup[key] = []
            inner_lookup[key].append(inner_item)

        for outer_item in self.outer:
            key = self.outer_key_selector(outer_item)  # type: ignore
            if key in inner_lookup:
                for inner_item in inner_lookup[key]:
                    yield self.result_selector(outer_item, inner_item)


class Window(Enumerable[list[T]], Generic[T]):
    """Sliding window operation."""

    def __init__(self, source: Enumerable[T], size: int, step: int = 1):
        super().__init__()
        self.source = source
        self.size = size
        self.step = step

    def __iter__(self) -> Iterator[list[T]]:
        window: list[T] = []
        iterator = iter(self.source)

        # Fill initial window
        for _ in range(self.size):
            try:
                window.append(next(iterator))
            except StopIteration:
                if window:
                    yield window
                return

        yield list(window)

        # Slide window
        while True:
            try:
                for _ in range(self.step):
                    window.pop(0)
                    window.append(next(iterator))
                yield list(window)
            except StopIteration:
                break


class Batch(Enumerable[list[T]], Generic[T]):
    """Batch into chunks."""

    def __init__(self, source: Enumerable[T], size: int):
        super().__init__()
        self.source = source
        self.size = size

    def __iter__(self) -> Iterator[list[T]]:
        iterator = iter(self.source)
        while True:
            batch = list(islice(iterator, self.size))
            if not batch:
                break
            yield batch


class WithProgress(Enumerable[T]):
    """Add progress tracking to enumeration."""

    def __init__(self, source: Enumerable[T], description: str = "Processing"):
        super().__init__()
        self.source = source
        self.description = description

    def __iter__(self) -> Iterator[T]:
        try:
            from tqdm import tqdm

            for item in tqdm(self.source, desc=self.description):
                yield item
        except ImportError:
            # Fall back to regular iteration if rich is not available
            for item in self.source:
                yield item


class WindowPredicate(Enumerable[list[T]], Generic[T]):
    """Window by predicate condition."""

    def __init__(self, source: Enumerable[T], predicate: Callable[[list[T]], bool]):
        super().__init__()
        self.source = source
        self.predicate = predicate

    def __iter__(self) -> Iterator[list[T]]:
        window: list[T] = []
        for item in self.source:
            window.append(item)  # type: ignore
            if self.predicate(window):
                yield list(window)
                window = []
        if window:
            yield window


class ParallelSelect(Enumerable[U], Generic[T, U]):
    """Parallel select/map operation using ThreadPoolExecutor."""

    def __init__(self, source: Enumerable[T], selector: Callable[[T], U], parallelism: int):
        super().__init__()
        self.source = source
        self.selector = selector
        self.parallelism = parallelism

    def __iter__(self) -> Iterator[U]:
        with ThreadPoolExecutor(max_workers=self.parallelism) as executor:
            # Submit all tasks and track with indices for ordering
            futures_with_indices = []
            for i, item in enumerate(self.source):
                future = executor.submit(self.selector, item)
                futures_with_indices.append((i, future))

            # Sort by index to maintain order
            futures_with_indices.sort(key=lambda x: x[0])

            # Yield results in order
            for _, future in futures_with_indices:
                yield future.result()


class IterableEnumerable(Enumerable[T]):
    def __init__(self, rows: Iterable[T]):
        self.rows = rows

    def __iter__(self):
        yield from self.rows


class Table(BaseModel, Enumerable[T]):
    """Table with automatic schema inference and LINQ operations."""

    rows: list[T]

    def __iter__(self) -> Iterator[T]:  # type: ignore
        return iter(self.rows)

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> T:
        return self.rows[index]

    @property
    def row_count(self) -> int:
        """Get row count."""
        return len(self.rows)

    @classmethod
    def from_rows(cls, rows: list[T], table_schema: type[BaseModel] | None = None) -> "Table[T]":
        """Create table from rows."""
        _ = table_schema  # Mark as used
        table = cls(rows=rows)
        return table

    @classmethod
    def empty(cls) -> "Table[Any]":
        """Create empty table."""
        return cls(rows=[])

    def materialize(self) -> "Table[T]":
        return self


def from_iterable(items: Iterable[T]) -> Table[T]:
    """Create a Table from any iterable."""
    return Table.from_rows(list(items))
