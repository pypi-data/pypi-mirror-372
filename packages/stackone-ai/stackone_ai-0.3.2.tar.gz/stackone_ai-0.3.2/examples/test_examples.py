import importlib.util
import sys
from pathlib import Path

import pytest
import responses


def get_example_files() -> list[str]:
    """Get all example files from the directory"""
    examples_dir = Path(__file__).parent
    examples = []

    for file in examples_dir.glob("*.py"):
        # Skip __init__.py and test files
        if file.name.startswith("__") or file.name.startswith("test_"):
            continue
        examples.append(file.name)

    return examples


EXAMPLES = get_example_files()

# Map of example files to required optional packages
OPTIONAL_DEPENDENCIES = {
    "openai_integration.py": ["openai"],
    "langchain_integration.py": ["langchain_openai"],
    "crewai_integration.py": ["crewai"],
}


def test_example_files_exist() -> None:
    """Verify that we found example files to test"""
    assert len(EXAMPLES) > 0, "No example files found"
    print(f"Found {len(EXAMPLES)} examples")


@pytest.mark.parametrize("example_file", EXAMPLES)
@responses.activate
def test_run_example(example_file: str) -> None:
    """Run each example file directly using python"""
    # Skip if optional dependencies are not available
    if example_file in OPTIONAL_DEPENDENCIES:
        for module in OPTIONAL_DEPENDENCIES[example_file]:
            try:
                __import__(module)
            except ImportError:
                pytest.skip(f"Skipping {example_file}: {module} not installed")

    # Setup mock responses for examples that need them
    if example_file in ["index.py", "file_uploads.py"]:
        # Mock employee list endpoint
        responses.add(
            responses.GET,
            "https://api.stackone.com/unified/hris/employees",
            json={
                "data": [
                    {
                        "id": "test-employee-1",
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john.doe@example.com"
                    }
                ]
            },
            status=200
        )

        # Mock document upload endpoint
        responses.add(
            responses.POST,
            "https://api.stackone.com/unified/hris/employees/c28xIQaWQ6MzM5MzczMDA2NzMzMzkwNzIwNA/documents/upload",
            json={"success": True, "document_id": "test-doc-123"},
            status=200
        )

    example_path = Path(__file__).parent / example_file

    # Import and run the example module directly
    spec = importlib.util.spec_from_file_location("example", example_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules["example"] = module
        spec.loader.exec_module(module)
