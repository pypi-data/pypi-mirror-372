"""
Test helpers and utilities for providing clear error messages to contributors.

This module provides custom assertions, error reporting, and debugging utilities
to help contributors understand test failures and fix issues quickly.
"""

import threading
import time
import traceback
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional


class ContributorFriendlyAssertions:
    """
    Custom assertions that provide clear, actionable error messages for contributors.

    These assertions go beyond basic pytest assertions to explain:
    - What was expected vs what actually happened
    - Why the assertion matters for the codebase
    - How to fix common issues
    - Context about the test scenario
    """

    @staticmethod
    def assert_context_item_immutable(
        original_list: List[str], context_item, field_name: str = "subscribers"
    ):
        """
        Assert that ContextItem properly copies mutable inputs to prevent external modification.

        Args:
            original_list: The original list that was passed to ContextItem
            context_item: The ContextItem instance to check
            field_name: Name of the field being tested

        Raises:
            AssertionError: With detailed explanation if immutability is violated
        """
        original_length = len(original_list)

        # Modify the original list
        original_list.append("test_modification")

        # Check if the context item was affected
        item_field = getattr(context_item, field_name)
        if len(item_field) != original_length:
            raise AssertionError(
                f"\n❌ IMMUTABILITY VIOLATION DETECTED!\n"
                f"📍 Issue: ContextItem.{field_name} is not properly isolated from external modifications\n"
                f"🔍 Expected: {field_name} length should remain {original_length} after external list modification\n"
                f"💥 Actual: {field_name} length is {len(item_field)} (was modified externally!)\n"
                f"📋 Current {field_name}: {item_field}\n"
                f"📋 Modified original: {original_list}\n\n"
                f"🔧 HOW TO FIX:\n"
                f"   In ContextItem.__init__, ensure you create a copy of mutable parameters:\n"
                f"   ✅ self.{field_name} = list({field_name}) if {field_name} else []\n"
                f"   ❌ self.{field_name} = {field_name}  # This creates a reference, not a copy!\n\n"
                f"💡 WHY THIS MATTERS:\n"
                f"   If ContextItem doesn't copy mutable inputs, external code can accidentally\n"
                f"   modify the context data, leading to hard-to-debug issues in production.\n"
                f"   This is a critical data integrity requirement for the Syntha SDK."
            )

    @staticmethod
    def assert_agent_access_control(
        mesh, key: str, agent: str, should_have_access: bool, context: str = ""
    ):
        """
        Assert that agent access control works correctly with clear error messages.

        Args:
            mesh: ContextMesh instance
            key: The context key being accessed
            agent: The agent attempting access
            should_have_access: Whether the agent should have access
            context: Additional context about the test scenario
        """
        try:
            result = mesh.get(key, agent)
            has_access = result is not None
        except Exception as e:
            raise AssertionError(
                f"\n❌ ACCESS CONTROL CHECK FAILED!\n"
                f"📍 Issue: Exception occurred while checking agent access\n"
                f"🔍 Agent: '{agent}'\n"
                f"🔍 Key: '{key}'\n"
                f"🔍 Context: {context}\n"
                f"💥 Exception: {type(e).__name__}: {e}\n\n"
                f"🔧 HOW TO FIX:\n"
                f"   Check that ContextMesh.get() handles edge cases properly:\n"
                f"   - Invalid agent names\n"
                f"   - Non-existent keys\n"
                f"   - Null/empty parameters\n"
            )

        if has_access != should_have_access:
            access_status = "HAS ACCESS" if has_access else "NO ACCESS"
            expected_status = (
                "SHOULD HAVE ACCESS" if should_have_access else "SHOULD NOT HAVE ACCESS"
            )

            raise AssertionError(
                f"\n❌ ACCESS CONTROL VIOLATION!\n"
                f"📍 Issue: Agent access permissions are not working correctly\n"
                f"🔍 Agent: '{agent}'\n"
                f"🔍 Key: '{key}'\n"
                f"🔍 Context: {context}\n"
                f"💥 Actual: Agent {access_status} (got: {result})\n"
                f"🎯 Expected: Agent {expected_status}\n\n"
                f"🔧 HOW TO FIX:\n"
                f"   Check the following in your ContextMesh implementation:\n"
                f"   1. Agent subscription logic in get() method\n"
                f"   2. Topic-based access control\n"
                f"   3. Proper routing validation\n"
                f"   4. Agent registration requirements\n\n"
                f"💡 WHY THIS MATTERS:\n"
                f"   Proper access control ensures agents only see data they're supposed to,\n"
                f"   which is critical for security and data isolation in multi-agent systems."
            )

    @staticmethod
    def assert_data_integrity(
        original_data: Any, retrieved_data: Any, operation: str = "storage/retrieval"
    ):
        """
        Assert that data maintains integrity through operations with detailed error reporting.

        Args:
            original_data: The data that was originally stored
            retrieved_data: The data that was retrieved
            operation: Description of the operation being tested
        """
        if original_data != retrieved_data:
            raise AssertionError(
                f"\n❌ DATA INTEGRITY VIOLATION!\n"
                f"📍 Issue: Data was modified during {operation}\n"
                f"🔍 Operation: {operation}\n"
                f"💥 Original:  {original_data} (type: {type(original_data).__name__})\n"
                f"💥 Retrieved: {retrieved_data} (type: {type(retrieved_data).__name__})\n\n"
                f"🔧 HOW TO FIX:\n"
                f"   1. Check serialization/deserialization logic\n"
                f"   2. Ensure deep copies are made when storing data\n"
                f"   3. Verify database schema matches data structure\n"
                f"   4. Check for encoding/decoding issues\n\n"
                f"💡 WHY THIS MATTERS:\n"
                f"   Data integrity is fundamental - if data changes unexpectedly,\n"
                f"   it can cause silent failures and corrupt agent interactions."
            )

    @staticmethod
    def assert_performance_within_limits(
        duration_seconds: float, max_seconds: float, operation: str, context: str = ""
    ):
        """
        Assert that operations complete within performance limits.

        Args:
            duration_seconds: Actual duration of the operation
            max_seconds: Maximum allowed duration
            operation: Description of the operation
            context: Additional context about the test
        """
        if duration_seconds > max_seconds:
            performance_ratio = duration_seconds / max_seconds
            raise AssertionError(
                f"\n❌ PERFORMANCE REGRESSION DETECTED!\n"
                f"📍 Issue: {operation} took too long to complete\n"
                f"🔍 Operation: {operation}\n"
                f"🔍 Context: {context}\n"
                f"💥 Actual Duration: {duration_seconds:.3f} seconds\n"
                f"🎯 Maximum Allowed: {max_seconds:.3f} seconds\n"
                f"📊 Performance Ratio: {performance_ratio:.2f}x slower than expected\n\n"
                f"🔧 HOW TO FIX:\n"
                f"   1. Profile the code to identify bottlenecks\n"
                f"   2. Check for inefficient database queries\n"
                f"   3. Look for unnecessary loops or redundant operations\n"
                f"   4. Consider caching frequently accessed data\n"
                f"   5. Verify algorithms have expected time complexity\n\n"
                f"💡 WHY THIS MATTERS:\n"
                f"   Performance regressions can make the SDK unusable in production.\n"
                f"   We maintain strict performance standards to ensure scalability."
            )


class ExecutionReporter:
    """
    Provides detailed test execution reporting for contributors.

    This class helps contributors understand what tests are running,
    why they might be failing, and what the expected behavior should be.
    """

    def __init__(self):
        self.test_start_time = None
        self.test_context = {}

    @contextmanager
    def test_scenario(
        self,
        scenario_name: str,
        description: str,
        expected_behavior: str = "",
        setup_notes: str = "",
    ):
        """
        Context manager for running test scenarios with clear reporting.

        Args:
            scenario_name: Name of the test scenario
            description: What this test is checking
            expected_behavior: What should happen if the code is correct
            setup_notes: Any important setup details
        """
        print(f"\n🧪 TEST SCENARIO: {scenario_name}")
        print(f"📋 Description: {description}")
        if expected_behavior:
            print(f"🎯 Expected: {expected_behavior}")
        if setup_notes:
            print(f"⚙️  Setup: {setup_notes}")
        print("─" * 60)

        self.test_start_time = time.time()
        self.test_context = {
            "scenario": scenario_name,
            "description": description,
            "expected": expected_behavior,
            "setup": setup_notes,
        }

        try:
            yield self
            duration = time.time() - self.test_start_time
            print(f"✅ PASSED: {scenario_name} ({duration:.3f}s)")
        except Exception as e:
            duration = time.time() - self.test_start_time
            print(f"❌ FAILED: {scenario_name} ({duration:.3f}s)")
            print(f"💥 Error: {type(e).__name__}: {e}")

            # Add context to the error
            if hasattr(e, "args") and e.args:
                if not str(e).startswith("\n❌"):  # If not already a detailed error
                    enhanced_error = (
                        f"\n❌ TEST FAILURE in {scenario_name}\n"
                        f"📋 What this test checks: {description}\n"
                        f"🎯 Expected behavior: {expected_behavior}\n"
                        f"💥 What went wrong: {e}\n"
                        f"⚙️  Test setup: {setup_notes}\n\n"
                        f"🔧 DEBUGGING TIPS:\n"
                        f"   1. Check if your implementation matches the expected behavior above\n"
                        f"   2. Add print statements to trace execution\n"
                        f"   3. Run this specific test with: pytest {self._get_current_test_name()} -v -s\n"
                        f"   4. Check the original error: {e}"
                    )
                    # Replace the original error message
                    e.args = (enhanced_error,)
            raise

    def _get_current_test_name(self):
        """Get the current test name from the call stack."""
        import inspect

        for frame_info in inspect.stack():
            if frame_info.function.startswith("test_"):
                return f"{frame_info.filename}::{frame_info.function}"
        return "unknown_test"

    def log_step(self, step: str, details: str = ""):
        """Log a test step for debugging."""
        print(f"   🔍 {step}")
        if details:
            print(f"      💡 {details}")

    def log_data(self, label: str, data: Any):
        """Log data values for debugging."""
        print(f"   📊 {label}: {data} (type: {type(data).__name__})")


def debug_context_mesh_state(mesh, label: str = "ContextMesh State"):
    """
    Debug utility to print the current state of a ContextMesh for troubleshooting.

    Args:
        mesh: ContextMesh instance to debug
        label: Label for the debug output
    """
    print(f"\n🔍 DEBUG: {label}")
    print("─" * 40)

    try:
        # Try to access internal state (adjust based on actual ContextMesh implementation)
        if hasattr(mesh, "_contexts"):
            print(f"📦 Total contexts: {len(mesh._contexts)}")
            for key, item in mesh._contexts.items():
                print(f"   🔑 '{key}': {item.value} (subscribers: {item.subscribers})")

        if hasattr(mesh, "_agent_topics"):
            print(f"👥 Agent topics: {mesh._agent_topics}")

        if hasattr(mesh, "_topic_subscribers"):
            print(f"📢 Topic subscribers: {mesh._topic_subscribers}")

    except Exception as e:
        print(f"⚠️  Could not debug mesh state: {e}")

    print("─" * 40)


def create_test_summary_report():
    """
    Create a summary report for contributors showing what areas need attention.
    """
    return """
    
🎯 CONTRIBUTOR TEST GUIDANCE
════════════════════════════

📋 WHEN TESTS FAIL, CHECK THESE COMMON ISSUES:

1️⃣  IMMUTABILITY VIOLATIONS
   - ContextItem should copy mutable inputs (lists, dicts)
   - Use list(input) or dict(input) to create copies
   - Never store references to mutable parameters

2️⃣  ACCESS CONTROL ISSUES  
   - Check agent subscription logic
   - Verify topic-based routing
   - Ensure proper permission validation

3️⃣  DATA INTEGRITY PROBLEMS
   - Verify serialization/deserialization  
   - Check for encoding issues
   - Ensure database schema matches data

4️⃣  PERFORMANCE REGRESSIONS
   - Profile slow operations
   - Check for inefficient queries
   - Look for unnecessary loops

5️⃣  CONCURRENCY ISSUES
   - Ensure thread safety
   - Check for race conditions
   - Verify proper locking

🔧 DEBUGGING WORKFLOW:
   1. Read the detailed error message
   2. Check the "HOW TO FIX" section
   3. Run the specific failing test with -v -s flags
   4. Add debug prints to trace execution
   5. Use the debug utilities in test_helpers.py

📞 NEED HELP?
   - Check existing tests for examples
   - Look at the test documentation
   - Review the contributor guidelines
   - Ask questions in the issue tracker

"""


# Export the main utilities
__all__ = [
    "ContributorFriendlyAssertions",
    "ExecutionReporter",
    "debug_context_mesh_state",
    "create_test_summary_report",
]
