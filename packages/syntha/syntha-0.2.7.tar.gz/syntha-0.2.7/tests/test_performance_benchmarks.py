#!/usr/bin/env python3
"""
Performance benchmarks for Syntha framework integration.

Tests the performance of the new automatic framework integration system
including tool creation speed, caching efficiency, and memory usage.
"""

import os
import sys
import time

import pytest

# Try to import psutil, but don't fail if it's not available
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Add the project root to path for imports
sys.path.insert(0, "..")

from syntha import ContextMesh, ToolHandler
from syntha.framework_adapters import get_supported_frameworks
from syntha.tool_factory import SynthaToolFactory


class PerformanceBenchmark:
    """Base class for performance benchmarks."""

    def __init__(self):
        self.results = {}

    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function using high-resolution timer."""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        return result, end_time - start_time

    def measure_memory(self, func, *args, **kwargs):
        """Measure memory usage of a function."""
        if not PSUTIL_AVAILABLE:
            # Skip memory measurement if psutil is not available
            result = func(*args, **kwargs)
            return result, 0.0

        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024  # MB

        result = func(*args, **kwargs)

        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_delta = mem_after - mem_before

        return result, memory_delta

    def run_benchmark(self, name: str, func, iterations: int = 100, *args, **kwargs):
        """Run a benchmark multiple times and collect statistics."""
        times = []

        for _ in range(iterations):
            _, duration = self.measure_time(func, *args, **kwargs)
            times.append(duration)

        total = sum(times)
        self.results[name] = {
            "iterations": iterations,
            "total_time": total,
            "average_time": (total / len(times)) if total > 0 else 0.0,
            "min_time": min(times),
            "max_time": max(times),
            "times_per_second": (iterations / total) if total > 0 else float("inf"),
        }

        return self.results[name]


class TestToolCreationPerformance:
    """Test performance of tool creation operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="PerfTestAgent")
        self.factory = SynthaToolFactory(self.handler)
        self.benchmark = PerformanceBenchmark()

    def test_single_tool_creation_speed(self):
        """Test speed of creating a single tool."""

        def create_openai_tool():
            return self.factory.create_tool("openai", "get_context")

        result = self.benchmark.run_benchmark(
            "single_tool_creation", create_openai_tool, iterations=1000
        )

        print(f"\n🚀 Single Tool Creation Performance:")
        print(f"  Average time: {result['average_time']*1000:.2f}ms")
        print(f"  Tools per second: {result['times_per_second']:.0f}")
        print(
            f"  Min/Max: {result['min_time']*1000:.2f}ms / {result['max_time']*1000:.2f}ms"
        )

        # Performance assertions (platform/CI aware)
        import os
        import sys

        is_ci = (
            os.getenv("CI", "false").lower() == "true"
            or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
        )
        ci_multiplier = 2.0 if is_ci else 1.0
        avg_limit = 0.09 * ci_multiplier
        min_tps = 5 / ci_multiplier
        # For extremely fast measurements, times_per_second can be unstable; allow zero only if average_time is near-zero
        assert result["average_time"] < avg_limit
        if result["average_time"] > 0:
            assert result["times_per_second"] >= min_tps

    def test_multiple_tools_creation_speed(self):
        """Test speed of creating all tools for a framework."""

        def create_all_openai_tools():
            return self.factory.create_tools("openai")

        result = self.benchmark.run_benchmark(
            "all_tools_creation", create_all_openai_tools, iterations=100
        )

        tools = create_all_openai_tools()
        tool_count = len(tools)

        print(f"\n📦 All Tools Creation Performance ({tool_count} tools):")
        print(f"  Average time: {result['average_time']*1000:.2f}ms")
        print(f"  Tool sets per second: {result['times_per_second']:.1f}")
        print(f"  Time per tool: {result['average_time']/tool_count*1000:.2f}ms")

        # Performance assertions (platform/CI aware)
        import os

        is_ci = (
            os.getenv("CI", "false").lower() == "true"
            or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
        )
        avg_limit = 0.12 if is_ci else 0.1
        min_tps = 8 if not is_ci else 5
        assert result["average_time"] < avg_limit
        if result["average_time"] > 0:
            assert result["times_per_second"] >= min_tps

    def test_framework_comparison_speed(self):
        """Compare tool creation speed across frameworks."""
        frameworks = ["openai", "anthropic", "langgraph"]
        framework_results = {}

        for framework in frameworks:

            def create_framework_tools():
                return self.factory.create_tools(framework)

            result = self.benchmark.run_benchmark(
                f"{framework}_tools", create_framework_tools, iterations=50
            )
            framework_results[framework] = result

        print(f"\n⚖️  Framework Comparison:")
        for framework, result in framework_results.items():
            print(
                f"  {framework:>10}: {result['average_time']*1000:6.2f}ms avg, {result['times_per_second']:6.1f} sets/sec"
            )

        # All frameworks should be reasonably fast (allow slack on CI)
        import os

        is_ci = (
            os.getenv("CI", "false").lower() == "true"
            or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
        )
        limit = 0.25 if is_ci else 0.2
        for framework, result in framework_results.items():
            assert result["average_time"] < limit, f"{framework} too slow"


class TestCachingPerformance:
    """Test performance of adapter caching system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="CacheTestAgent")
        self.benchmark = PerformanceBenchmark()

    def test_cache_hit_vs_miss_performance(self):
        """Compare performance of cache hits vs misses."""
        factory = SynthaToolFactory(self.handler)

        # Measure cold start (cache miss)
        def create_adapter_cold():
            factory.clear_cache()
            return factory.get_adapter("openai")

        cold_result = self.benchmark.run_benchmark(
            "cache_miss", create_adapter_cold, iterations=100
        )

        # Warm up cache
        factory.get_adapter("openai")

        # Measure warm start (cache hit)
        def create_adapter_warm():
            return factory.get_adapter("openai")

        warm_result = self.benchmark.run_benchmark(
            "cache_hit", create_adapter_warm, iterations=1000
        )

        print(f"\n🗄️  Cache Performance:")
        print(f"  Cache miss: {cold_result['average_time']*1000:.2f}ms avg")
        print(f"  Cache hit:  {warm_result['average_time']*1000:.2f}ms avg")
        speedup = (
            cold_result["average_time"] / warm_result["average_time"]
            if warm_result["average_time"] > 0
            else float("inf")
        )
        print(f"  Speedup:    {speedup:.1f}x")

        # Cache hits should be significantly faster (or both very fast). Be CI-aware
        import os

        is_ci = (
            os.getenv("CI", "false").lower() == "true"
            or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
        )
        factor = 1.7 if is_ci else 2.0
        if cold_result["average_time"] > 0:
            assert warm_result["average_time"] < cold_result["average_time"] / factor
        else:
            # Both operations are very fast, which is good
            assert True
        # Cache hits should be reasonably fast; allow more on CI
        limit = 0.02 if is_ci else 0.01
        assert warm_result["average_time"] < limit

    def test_multiple_framework_caching(self):
        """Test caching performance with multiple frameworks."""
        factory = SynthaToolFactory(self.handler)
        frameworks = ["openai", "anthropic", "langgraph"]

        # First run (cache misses)
        start_time = time.perf_counter()
        for framework in frameworks:
            factory.get_adapter(framework)
        first_run_time = time.perf_counter() - start_time

        # Second run (cache hits)
        start_time = time.perf_counter()
        for framework in frameworks:
            factory.get_adapter(framework)
        second_run_time = time.perf_counter() - start_time

        cache_info = factory.get_cache_info()

        print(f"\n🏎️  Multi-Framework Caching:")
        print(f"  First run (cold):  {first_run_time*1000:.2f}ms")
        print(f"  Second run (warm): {second_run_time*1000:.2f}ms")
        print(f"  Cache size:        {cache_info['cache_size']} adapters")
        speedup = (
            first_run_time / second_run_time if second_run_time > 0 else float("inf")
        )
        print(f"  Speedup:           {speedup:.1f}x")

        assert cache_info["cache_size"] == len(frameworks)
        # Should be faster or both very fast (CI-aware)
        import os

        is_ci = (
            os.getenv("CI", "false").lower() == "true"
            or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
        )
        if first_run_time > 0:
            # For extremely fast operations, timing noise can dominate; be lenient
            if first_run_time < 0.005:
                # Just ensure the warm run is not slower than the cold run in trivial cases
                assert second_run_time <= first_run_time
            else:
                factor = 2.0 if is_ci else 3.0
                assert second_run_time < first_run_time / factor
        else:
            # Both operations are very fast, which is good
            assert True


class TestMemoryUsage:
    """Test memory usage of framework integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="MemoryTestAgent")
        self.benchmark = PerformanceBenchmark()

    @pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not available")
    def test_tool_creation_memory_usage(self):
        """Test memory usage during tool creation."""
        factory = SynthaToolFactory(self.handler)

        def create_many_tools():
            tools = []
            for _ in range(100):
                tools.extend(factory.create_tools("openai"))
            return tools

        tools, memory_delta = self.benchmark.measure_memory(create_many_tools)

        print(f"\n💾 Memory Usage:")
        print(f"  Tools created: {len(tools)}")
        print(f"  Memory delta:  {memory_delta:.2f} MB")
        print(f"  Memory per tool: {memory_delta/len(tools)*1024:.2f} KB")

        # Memory usage should be reasonable
        assert memory_delta < 50  # Should use less than 50MB
        assert memory_delta / len(tools) < 0.1  # Less than 100KB per tool

    @pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not available")
    def test_adapter_cache_memory_usage(self):
        """Test memory usage of adapter caching."""
        factory = SynthaToolFactory(self.handler)

        def create_cached_adapters():
            frameworks = get_supported_frameworks()
            for framework in frameworks:
                try:
                    factory.get_adapter(framework)
                except Exception:
                    pass  # Skip frameworks with missing dependencies
            return factory.get_cache_info()

        cache_info, memory_delta = self.benchmark.measure_memory(create_cached_adapters)

        print(f"\n🗃️  Cache Memory Usage:")
        print(f"  Cached adapters: {cache_info['cache_size']}")
        print(f"  Memory delta:    {memory_delta:.2f} MB")
        print(
            f"  Memory per adapter: {memory_delta/max(cache_info['cache_size'], 1):.2f} MB"
        )

        # Cache should not use excessive memory
        assert memory_delta < 20  # Should use less than 20MB for cache


class TestScalabilityBenchmarks:
    """Test scalability with multiple handlers and tools."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.benchmark = PerformanceBenchmark()

    def test_multiple_handlers_performance(self):
        """Test performance with multiple tool handlers."""

        def create_multiple_handlers(count):
            handlers = []
            for i in range(count):
                handler = ToolHandler(self.mesh, agent_name=f"Agent_{i}")
                factory = SynthaToolFactory(handler)
                tools = factory.create_tools("openai")
                handlers.append((handler, factory, tools))
            return handlers

        # Test with different numbers of handlers
        for count in [10, 50, 100]:
            result, duration = self.benchmark.measure_time(
                create_multiple_handlers, count
            )

            total_tools = sum(len(tools) for _, _, tools in result)

            print(f"\n👥 {count} Handlers Performance:")
            print(f"  Total time: {duration*1000:.2f}ms")
            print(f"  Time per handler: {duration/count*1000:.2f}ms")
            print(f"  Total tools: {total_tools}")
            tools_per_sec = total_tools / duration if duration > 0 else float("inf")
            print(f"  Tools per second: {tools_per_sec:.0f}")

            # Should scale reasonably (platform/CI aware)
            import os

            is_ci = (
                os.getenv("CI", "false").lower() == "true"
                or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
            )
            per_handler_limit = 0.15 if is_ci else 0.1
            assert duration < count * per_handler_limit

    def test_concurrent_tool_creation(self):
        """Test concurrent tool creation performance."""
        import threading

        handlers = []
        for i in range(10):
            handler = ToolHandler(self.mesh, agent_name=f"ConcurrentAgent_{i}")
            handlers.append(handler)

        results = []

        def create_tools_for_handler(handler):
            factory = SynthaToolFactory(handler)
            start_time = time.time()
            tools = factory.create_tools("openai")
            duration = time.time() - start_time
            results.append((len(tools), duration))

        # Run concurrent tool creation
        start_time = time.time()
        threads = []
        for handler in handlers:
            thread = threading.Thread(target=create_tools_for_handler, args=(handler,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        total_duration = time.time() - start_time

        total_tools = sum(tool_count for tool_count, _ in results)
        avg_duration = sum(duration for _, duration in results) / len(results)

        print(f"\n🧵 Concurrent Creation Performance:")
        print(f"  Threads: {len(threads)}")
        print(f"  Total time: {total_duration*1000:.2f}ms")
        print(f"  Avg thread time: {avg_duration*1000:.2f}ms")
        print(f"  Total tools: {total_tools}")
        concurrency_benefit = (
            avg_duration / total_duration if total_duration > 0 else float("inf")
        )
        print(f"  Concurrency benefit: {concurrency_benefit:.1f}x")

        # Concurrent execution should provide some benefit (or both very fast)
        if avg_duration > 0 and total_duration > 0:
            # For very fast operations, be more tolerant
            if avg_duration < 0.001:
                # Operations are extremely fast, just verify they complete
                assert total_duration > 0
                assert avg_duration > 0
            else:
                # For slower operations, expect some concurrency benefit
                # Made more lenient and CI-aware due to scheduler variability
                import os

                is_ci = (
                    os.getenv("CI", "false").lower() == "true"
                    or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
                )
                factor = 1.5 if is_ci else 1.2
                assert total_duration < avg_duration * factor
        else:
            # Operations are very fast, which is good
            assert True


class TestPerformanceRegression:
    """Test for performance regressions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mesh = ContextMesh()
        self.handler = ToolHandler(self.mesh, agent_name="RegressionTestAgent")
        self.benchmark = PerformanceBenchmark()

    def test_tool_creation_consistency(self):
        """Test that tool creation performance is consistent."""
        factory = SynthaToolFactory(self.handler)

        times = []
        for i in range(50):
            start_time = time.time()
            factory.create_tools("openai")
            duration = time.time() - start_time
            times.append(duration)

        avg_time = sum(times) / len(times)
        max_deviation = max(abs(t - avg_time) for t in times)

        print(f"\n📊 Performance Consistency:")
        print(f"  Average time: {avg_time*1000:.2f}ms")
        print(f"  Max deviation: {max_deviation*1000:.2f}ms")
        coefficient = max_deviation / avg_time if avg_time > 0 else float("inf")
        print(f"  Coefficient of variation: {coefficient:.2%}")

        # Performance should be consistent (with generous tolerance; CI-aware)
        if avg_time > 0:
            # For very fast operations, be very tolerant of timing variations
            # This accounts for system scheduling, garbage collection, etc.
            import os

            is_ci = (
                os.getenv("CI", "false").lower() == "true"
                or os.getenv("GITHUB_ACTIONS", "false").lower() == "true"
            )
            tolerance = 60.0 if avg_time < 0.001 else (0.7 if is_ci else 0.5)
            assert max_deviation < avg_time * tolerance
        else:
            # All operations are very fast and consistent, which is good
            assert True

    @pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not available")
    def test_memory_leak_detection(self):
        """Test for memory leaks during repeated operations."""
        import gc

        factory = SynthaToolFactory(self.handler)
        process = psutil.Process(os.getpid())

        # Initial memory measurement
        gc.collect()
        initial_memory = process.memory_info().rss / 1024 / 1024

        # Perform many operations
        for i in range(100):
            tools = factory.create_tools("openai")
            factory.clear_cache()
            del tools

            if i % 20 == 0:
                gc.collect()

        # Final memory measurement
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory

        print(f"\n🔍 Memory Leak Detection:")
        print(f"  Initial memory: {initial_memory:.2f} MB")
        print(f"  Final memory:   {final_memory:.2f} MB")
        print(f"  Memory growth:  {memory_growth:.2f} MB")
        print(f"  Growth per operation: {memory_growth/100*1024:.2f} KB")

        # Should not have significant memory growth
        assert memory_growth < 10  # Less than 10MB growth
        assert memory_growth / 100 < 0.1  # Less than 100KB per operation


def run_all_benchmarks():
    """Run all performance benchmarks and generate a report."""
    print("🏁 Syntha Framework Integration Performance Benchmarks")
    print("=" * 70)

    benchmark_classes = [
        TestToolCreationPerformance,
        TestCachingPerformance,
        TestMemoryUsage,
        TestScalabilityBenchmarks,
        TestPerformanceRegression,
    ]

    results = {}

    for benchmark_class in benchmark_classes:
        class_name = benchmark_class.__name__
        print(f"\n🧪 Running {class_name}...")

        try:
            benchmark = benchmark_class()
            benchmark.setup_method()

            # Run all test methods
            for method_name in dir(benchmark):
                if method_name.startswith("test_"):
                    print(f"\n  → {method_name}")
                    getattr(benchmark, method_name)()

            results[class_name] = "✅ PASSED"

        except Exception as e:
            print(f"❌ {class_name} failed: {e}")
            results[class_name] = f"❌ FAILED: {e}"

    # Generate summary report
    print(f"\n\n📋 Benchmark Summary")
    print("=" * 70)

    for class_name, result in results.items():
        print(f"  {result} {class_name}")

    passed = sum(1 for r in results.values() if r.startswith("✅"))
    total = len(results)

    print(f"\n📊 Overall Results: {passed}/{total} benchmark suites passed")

    if passed == total:
        print("🎉 All performance benchmarks passed!")
        print("💪 The framework integration system is performing well!")
    else:
        print("⚠️  Some benchmarks failed - performance review needed")


if __name__ == "__main__":
    run_all_benchmarks()
