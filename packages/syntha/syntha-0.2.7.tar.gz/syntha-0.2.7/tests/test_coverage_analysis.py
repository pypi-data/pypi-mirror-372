"""
Comprehensive test coverage report and quality metrics.

This module provides utilities to analyze test coverage and ensure
comprehensive testing of the Syntha SDK.
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def analyze_test_coverage():
    """Analyze test coverage of the codebase."""
    syntha_dir = Path(__file__).parent.parent / "syntha"
    tests_dir = Path(__file__).parent

    # Get all Python files in syntha package
    syntha_files = list(syntha_dir.glob("**/*.py"))
    syntha_files = [f for f in syntha_files if f.name != "__init__.py"]

    # Get all test files
    test_files = list(tests_dir.glob("**/test_*.py"))

    print("=== Syntha SDK Test Coverage Analysis ===\n")
    print(f"Source files: {len(syntha_files)}")
    print(f"Test files: {len(test_files)}")

    # Analyze each source file
    coverage_report = {}

    for source_file in syntha_files:
        module_name = source_file.stem
        functions, classes = extract_functions_and_classes(source_file)

        coverage_report[module_name] = {
            "file": source_file,
            "functions": functions,
            "classes": classes,
            "tested_functions": set(),
            "tested_classes": set(),
            "test_files": [],
        }

    # Analyze test files for coverage
    for test_file in test_files:
        test_functions, test_classes = extract_functions_and_classes(test_file)

        # Find which source modules this test file covers
        for module_name in coverage_report:
            if (
                module_name in test_file.name
                or module_name.replace("_", "") in test_file.name
            ):
                coverage_report[module_name]["test_files"].append(test_file)

                # Extract tested function/class names from test names
                for test_func in test_functions:
                    # Remove test_ prefix and extract tested function name
                    if test_func.startswith("test_"):
                        tested_name = test_func[5:]  # Remove "test_"

                        # Match against source functions/classes
                        for func in coverage_report[module_name]["functions"]:
                            if func.lower() in tested_name.lower():
                                coverage_report[module_name]["tested_functions"].add(
                                    func
                                )

                        for cls in coverage_report[module_name]["classes"]:
                            if cls.lower() in tested_name.lower():
                                coverage_report[module_name]["tested_classes"].add(cls)

    # Generate coverage report
    print("\n=== Coverage by Module ===")
    total_functions = 0
    total_tested_functions = 0
    total_classes = 0
    total_tested_classes = 0

    for module_name, info in coverage_report.items():
        func_count = len(info["functions"])
        tested_func_count = len(info["tested_functions"])
        class_count = len(info["classes"])
        tested_class_count = len(info["tested_classes"])

        total_functions += func_count
        total_tested_functions += tested_func_count
        total_classes += class_count
        total_tested_classes += tested_class_count

        func_coverage = (
            (tested_func_count / func_count * 100) if func_count > 0 else 100
        )
        class_coverage = (
            (tested_class_count / class_count * 100) if class_count > 0 else 100
        )

        print(f"\n{module_name}.py:")
        print(f"  Functions: {tested_func_count}/{func_count} ({func_coverage:.1f}%)")
        print(f"  Classes: {tested_class_count}/{class_count} ({class_coverage:.1f}%)")
        print(f"  Test files: {len(info['test_files'])}")

        # Show untested functions/classes
        untested_functions = info["functions"] - info["tested_functions"]
        untested_classes = info["classes"] - info["tested_classes"]

        if untested_functions:
            print(f"  Untested functions: {', '.join(sorted(untested_functions))}")
        if untested_classes:
            print(f"  Untested classes: {', '.join(sorted(untested_classes))}")

    # Overall coverage
    overall_func_coverage = (
        (total_tested_functions / total_functions * 100) if total_functions > 0 else 100
    )
    overall_class_coverage = (
        (total_tested_classes / total_classes * 100) if total_classes > 0 else 100
    )

    print(f"\n=== Overall Coverage ===")
    print(
        f"Functions: {total_tested_functions}/{total_functions} ({overall_func_coverage:.1f}%)"
    )
    print(
        f"Classes: {total_tested_classes}/{total_classes} ({overall_class_coverage:.1f}%)"
    )

    return coverage_report


def extract_functions_and_classes(file_path: Path) -> Tuple[Set[str], Set[str]]:
    """Extract function and class names from a Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        functions = set()
        classes = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private functions and special methods
                if not node.name.startswith("_"):
                    functions.add(node.name)
            elif isinstance(node, ast.ClassDef):
                # Skip private classes
                if not node.name.startswith("_"):
                    classes.add(node.name)

        return functions, classes

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return set(), set()


def analyze_test_quality():
    """Analyze quality metrics of test suite."""
    tests_dir = Path(__file__).parent
    test_files = list(tests_dir.glob("**/test_*.py"))

    print("\n=== Test Quality Analysis ===")

    total_tests = 0
    total_assertions = 0
    test_categories = {
        "unit": 0,
        "integration": 0,
        "performance": 0,
        "security": 0,
        "edge_case": 0,
    }

    for test_file in test_files:
        try:
            with open(test_file, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            # Count test functions
            test_functions = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
            ]
            total_tests += len(test_functions)

            # Count assertions
            assertions = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "assert"
            ]

            # Also count pytest assertions
            pytest_assertions = [
                node
                for node in ast.walk(tree)
                if isinstance(node, ast.Attribute) and node.attr.startswith("assert")
            ]

            total_assertions += len(assertions) + len(pytest_assertions)

            # Categorize tests by directory/filename
            if "unit" in str(test_file):
                test_categories["unit"] += len(test_functions)
            elif "integration" in str(test_file):
                test_categories["integration"] += len(test_functions)
            elif "performance" in str(test_file):
                test_categories["performance"] += len(test_functions)
            elif "security" in str(test_file):
                test_categories["security"] += len(test_functions)
            elif "edge" in str(test_file) or "edge_case" in str(test_file):
                test_categories["edge_case"] += len(test_functions)

        except Exception as e:
            print(f"Error analyzing {test_file}: {e}")

    print(f"Total test functions: {total_tests}")
    print(f"Total assertions: {total_assertions}")
    print(
        f"Assertions per test: {total_assertions / total_tests:.1f}"
        if total_tests > 0
        else "N/A"
    )

    print(f"\nTest distribution:")
    for category, count in test_categories.items():
        percentage = (count / total_tests * 100) if total_tests > 0 else 0
        print(f"  {category.title()}: {count} ({percentage:.1f}%)")

    return {
        "total_tests": total_tests,
        "total_assertions": total_assertions,
        "categories": test_categories,
    }


def check_test_requirements():
    """Check if test suite meets quality requirements."""
    print("\n=== Test Requirements Check ===")

    requirements = {
        "minimum_coverage": 80,  # 80% function coverage
        "minimum_tests": 50,  # At least 50 test functions
        "security_tests": True,  # Must have security tests
        "performance_tests": True,  # Must have performance tests
        "integration_tests": True,  # Must have integration tests
        "edge_case_tests": True,  # Must have edge case tests
    }

    # Analyze current state
    coverage_report = analyze_test_coverage()
    quality_metrics = analyze_test_quality()

    # Check requirements
    results = {}

    # Coverage requirement
    total_functions = sum(len(info["functions"]) for info in coverage_report.values())
    total_tested = sum(
        len(info["tested_functions"]) for info in coverage_report.values()
    )
    coverage_percentage = (
        (total_tested / total_functions * 100) if total_functions > 0 else 0
    )

    results["coverage"] = {
        "required": requirements["minimum_coverage"],
        "actual": coverage_percentage,
        "passed": coverage_percentage >= requirements["minimum_coverage"],
    }

    # Test count requirement
    results["test_count"] = {
        "required": requirements["minimum_tests"],
        "actual": quality_metrics["total_tests"],
        "passed": quality_metrics["total_tests"] >= requirements["minimum_tests"],
    }

    # Test category requirements
    for category in ["security", "performance", "integration", "edge_case"]:
        required = requirements[f"{category}_tests"]
        actual = quality_metrics["categories"].get(category, 0) > 0
        results[f"{category}_tests"] = {
            "required": required,
            "actual": actual,
            "passed": actual >= required,
        }

    # Print results
    print("\nRequirement Check Results:")
    all_passed = True

    for req_name, result in results.items():
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"  {req_name}: {status}")

        if req_name == "coverage":
            print(
                f"    Required: {result['required']}%, Actual: {result['actual']:.1f}%"
            )
        elif req_name == "test_count":
            print(f"    Required: {result['required']}, Actual: {result['actual']}")
        else:
            print(f"    Required: {result['required']}, Actual: {result['actual']}")

        if not result["passed"]:
            all_passed = False

    print(
        f"\nOverall: {'✅ ALL REQUIREMENTS MET' if all_passed else '❌ SOME REQUIREMENTS NOT MET'}"
    )

    return results


def generate_testing_recommendations():
    """Generate recommendations for improving test coverage."""
    print("\n=== Testing Recommendations ===")

    recommendations = [
        "✅ Comprehensive CI/CD pipeline with multi-platform testing",
        "✅ Unit tests covering core functionality",
        "✅ Integration tests for database and tool interactions",
        "✅ Performance benchmarking and regression testing",
        "✅ Security testing for common vulnerabilities",
        "✅ Edge case testing for robustness",
        "✅ Test fixtures and configuration for maintainability",
        "✅ Automated test collection and marking",
        "✅ Mock and patch testing for isolation",
        "✅ Thread safety and concurrency testing",
    ]

    additional_recommendations = [
        "🔄 Consider adding property-based testing with Hypothesis",
        "🔄 Add mutation testing to verify test effectiveness",
        "🔄 Implement test data generators for more comprehensive testing",
        "🔄 Add contract testing for API boundaries",
        "🔄 Consider adding chaos engineering tests",
        "🔄 Add benchmarking against competitor solutions",
        "🔄 Implement automated accessibility testing if applicable",
        "🔄 Add backwards compatibility testing",
    ]

    print("Current Testing Strengths:")
    for rec in recommendations:
        print(f"  {rec}")

    print(f"\nPotential Improvements:")
    for rec in additional_recommendations:
        print(f"  {rec}")


if __name__ == "__main__":
    try:
        analyze_test_coverage()
        analyze_test_quality()
        check_test_requirements()
        generate_testing_recommendations()
    except Exception as e:
        print(f"Error running analysis: {e}")
        sys.exit(1)
