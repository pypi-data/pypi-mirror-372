import pytest

from tidylinq.linq import Table, from_iterable


class TestBasicCreationAndIteration:
    def test_table_from_rows(self):
        table = Table.from_rows([1, 2, 3])
        assert list(table) == [1, 2, 3]

    def test_from_iterable(self):
        table = from_iterable([1, 2, 3])
        assert list(table) == [1, 2, 3]

    def test_empty_table(self):
        table = Table.empty()
        assert list(table) == []

    def test_table_len_and_indexing(self):
        table = Table.from_rows([10, 20, 30])
        assert len(table) == 3
        assert table[0] == 10
        assert table[2] == 30


class TestCoreTransformations:
    def test_select(self):
        table = Table.from_rows([1, 2, 3])
        result = table.select(lambda x: x * 2)
        assert list(result) == [2, 4, 6]

    def test_where(self):
        table = Table.from_rows([1, 2, 3, 4, 5])
        result = table.where(lambda x: x % 2 == 0)
        assert list(result) == [2, 4]

    def test_select_many(self):
        table = Table.from_rows([[1, 2], [3, 4], [5]])
        result = table.select_many(lambda x: x)
        assert list(result) == [1, 2, 3, 4, 5]

    def test_chaining_operations(self):
        table = Table.from_rows([1, 2, 3, 4, 5])
        result = table.where(lambda x: x > 2).select(lambda x: x * 10)
        assert list(result) == [30, 40, 50]


class TestAggregations:
    def test_count(self):
        table = Table.from_rows([1, 2, 3, 4, 5])
        assert table.count() == 5
        assert table.count(lambda x: x > 3) == 2

    def test_first(self):
        table = Table.from_rows([1, 2, 3, 4, 5])
        assert table.first() == 1
        assert table.first(lambda x: x > 3) == 4
        assert table.first(lambda x: x > 10, default=99) == 99

    def test_first_no_match_raises(self):
        table = Table.from_rows([1, 2, 3])
        with pytest.raises(ValueError, match="no matching element"):
            table.first(lambda x: x > 10)

    def test_last(self):
        table = Table.from_rows([1, 2, 3, 4, 5])
        assert table.last() == 5
        assert table.last(lambda x: x < 4) == 3
        assert table.last(lambda x: x > 10, default=99) == 99

    def test_last_no_match_raises(self):
        table = Table.from_rows([1, 2, 3])
        with pytest.raises(ValueError, match="no matching element"):
            table.last(lambda x: x > 10)

    def test_any(self):
        table = Table.from_rows([1, 2, 3])
        assert table.any() is True
        assert table.any(lambda x: x > 2) is True
        assert table.any(lambda x: x > 10) is False

    def test_any_empty(self):
        table = Table.empty()
        assert table.any() is False

    def test_all(self):
        table = Table.from_rows([2, 4, 6])
        assert table.all(lambda x: x % 2 == 0) is True
        assert table.all(lambda x: x > 1) is True
        assert table.all(lambda x: x > 3) is False

    def test_sum(self):
        table = Table.from_rows([1, 2, 3, 4])
        assert table.sum() == 10

    def test_average(self):
        table = Table.from_rows([2, 4, 6])
        assert table.average() == 4.0

    def test_average_empty_raises(self):
        table = Table.empty()
        with pytest.raises(ValueError, match="empty sequence"):
            table.average()

    def test_min_max(self):
        table = Table.from_rows([3, 1, 4, 2])
        assert table.min() == 1
        assert table.max() == 4


class TestSetOperations:
    def test_distinct(self):
        table = Table.from_rows([1, 2, 2, 3, 3, 3])
        result = table.distinct()
        assert list(result) == [1, 2, 3]

    def test_union(self):
        table1 = Table.from_rows([1, 2, 3])
        table2 = Table.from_rows([3, 4, 5])
        result = table1.union(table2)
        assert set(result) == {1, 2, 3, 4, 5}

    def test_intersect(self):
        table1 = Table.from_rows([1, 2, 3, 4])
        table2 = Table.from_rows([3, 4, 5, 6])
        result = table1.intersect(table2)
        assert list(result) == [3, 4]

    def test_except(self):
        table1 = Table.from_rows([1, 2, 3, 4])
        table2 = Table.from_rows([3, 4, 5])
        result = table1.except_(table2)
        assert list(result) == [1, 2]


class TestOrderingAndGrouping:
    def test_order_by(self):
        table = Table.from_rows([3, 1, 4, 2])
        result = table.order_by(lambda x: x)
        assert list(result) == [1, 2, 3, 4]

    def test_order_by_descending(self):
        table = Table.from_rows([3, 1, 4, 2])
        result = table.order_by_descending(lambda x: x)
        assert list(result) == [4, 3, 2, 1]

    def test_group_by(self):
        table = Table.from_rows([1, 2, 3, 4, 5, 6])
        result = table.group_by(lambda x: x % 2)
        groups = list(result)

        assert len(groups) == 2

        # Find even and odd groups
        even_group = next(g for g in groups if g.key == 0)
        odd_group = next(g for g in groups if g.key == 1)

        assert list(even_group) == [2, 4, 6]
        assert list(odd_group) == [1, 3, 5]
        assert even_group.count() == 3
        assert odd_group.count() == 3


class TestPartitioning:
    def test_take(self):
        table = Table.from_rows([1, 2, 3, 4, 5])
        result = table.take(3)
        assert list(result) == [1, 2, 3]

    def test_take_more_than_available(self):
        table = Table.from_rows([1, 2])
        result = table.take(5)
        assert list(result) == [1, 2]

    def test_skip(self):
        table = Table.from_rows([1, 2, 3, 4, 5])
        result = table.skip(2)
        assert list(result) == [3, 4, 5]

    def test_skip_more_than_available(self):
        table = Table.from_rows([1, 2])
        result = table.skip(5)
        assert list(result) == []

    def test_batch(self):
        table = Table.from_rows([1, 2, 3, 4, 5, 6, 7])
        result = table.batch(3)
        batches = list(result)
        assert batches == [[1, 2, 3], [4, 5, 6], [7]]


class TestEdgeCases:
    def test_empty_sequence_operations(self):
        table = Table.empty()

        assert list(table.select(lambda x: x * 2)) == []
        assert list(table.where(lambda x: x > 0)) == []
        assert table.count() == 0
        assert table.any() is False
        assert table.all(lambda x: x > 0) is True  # vacuously true

    def test_single_element_operations(self):
        table = Table.from_rows([42])

        assert table.first() == 42
        assert table.last() == 42
        assert table.count() == 1
        assert table.sum() == 42
        assert table.average() == 42.0

    def test_deferred_evaluation(self):
        table = Table.from_rows([1, 2, 3])

        # Operations should return new enumerable objects, not execute immediately
        mapped = table.select(lambda x: x * 2)
        filtered = mapped.where(lambda x: x > 2)

        # Only when we iterate should computation happen
        result = list(filtered)
        assert result == [4, 6]


class TestUtilityMethods:
    def test_to_list(self):
        table = Table.from_rows([1, 2, 3])
        result = table.select(lambda x: x * 2).to_list()
        assert result == [2, 4, 6]

    def test_partition(self):
        table = Table.from_rows([1, 2, 3, 4, 5])
        evens, odds = table.partition(lambda x: x % 2 == 0)
        assert list(evens) == [2, 4]
        assert list(odds) == [1, 3, 5]

    def test_materialize(self):
        table = Table.from_rows([1, 2, 3])
        materialized = table.select(lambda x: x * 2).materialize()
        assert isinstance(materialized, Table)
        assert list(materialized) == [2, 4, 6]

    def test_try_select_sequential(self):
        table = Table.from_rows([1, 2, 3, 4, 5])

        def sometimes_fails(x: int) -> int:
            if x == 3:
                raise ValueError(f"Failed on {x}")
            return x * 2

        successes, errors = table.try_select(sometimes_fails)

        assert list(successes) == [2, 4, 8, 10]
        assert len(list(errors)) == 1
        assert isinstance(list(errors)[0], ValueError)

    def test_try_select_parallel(self):
        table = Table.from_rows([1, 2, 3, 4, 5])

        def sometimes_fails(x: int) -> int:
            if x == 3:
                raise ValueError(f"Failed on {x}")
            return x * 2

        successes, errors = table.try_select(sometimes_fails, parallelism=2)

        # Results should be the same as sequential
        assert sorted(list(successes)) == [2, 4, 8, 10]
        assert len(list(errors)) == 1
        assert isinstance(list(errors)[0], ValueError)

    def test_parallel_map(self):
        """Test that parallel map works correctly."""
        import time

        def slow_square(x: int) -> int:
            """Simulate a slow operation."""
            time.sleep(0.05)  # Shorter sleep for tests
            return x * x

        numbers = Table.from_rows(range(10))

        # Sequential execution
        start = time.time()
        sequential_result = numbers.map(slow_square).to_list()
        sequential_time = time.time() - start

        # Parallel execution with 4 threads
        start = time.time()
        parallel_result = numbers.select(slow_square, parallelism=4).to_list()
        parallel_time = time.time() - start

        # Verify results are the same and in order
        assert sequential_result == parallel_result
        assert sequential_result == [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

        # Parallel should be faster
        assert parallel_time < sequential_time

    def test_progress_tracking_with_known_length(self):
        """Test that progress tracking works with enumerable chains that have known lengths."""
        # This simulates the scenario from examples/translation.py
        words = ["hello", "world", "test"]

        # Create an enumerable chain similar to the translation example
        enumerable_chain = (
            from_iterable(words)
            .map(lambda w: w.upper())  # Simple transformation instead of LLM call
            .with_progress(f"Processing {len(words)} words")
        )

        # The enumerable chain should have a __len__ method
        assert hasattr(enumerable_chain, "__len__")
        assert len(enumerable_chain) == 3

        # Materialize the results - this should show progress with known total
        results = enumerable_chain.to_list()
        assert results == ["HELLO", "WORLD", "TEST"]

    def test_enumerable_chain_preserves_length(self):
        """Test that chained operations preserve length information when possible."""
        # Start with a known-length iterable
        original = from_iterable(range(10))
        assert hasattr(original, "__len__")
        assert len(original) == 10

        # Map operation should preserve length
        mapped = original.map(lambda x: x * 2)
        assert hasattr(mapped, "__len__")
        assert len(mapped) == 10

        # Select operation should preserve length (map is alias for select)
        selected = original.select(lambda x: x + 1)
        assert hasattr(selected, "__len__")
        assert len(selected) == 10

        # Batch operation should calculate correct length
        batched = original.batch(3)
        assert hasattr(batched, "__len__")
        assert len(batched) == 4  # ceil(10/3) = 4 batches

        # Take operation doesn't preserve length info because it changes the actual length
        # taken = original.take(5)  # Take doesn't add __len__ because it changes the actual length

        # Chain multiple operations
        chained = original.map(lambda x: x * 2).map(lambda x: x + 1)
        assert hasattr(chained, "__len__")
        assert len(chained) == 10
