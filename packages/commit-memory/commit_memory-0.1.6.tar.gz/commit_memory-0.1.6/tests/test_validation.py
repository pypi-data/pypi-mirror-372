"""
Test script for validating the input validation functionality.

This script tests the validation functions and their integration with the MemoService.
"""

import os
import sys
from pathlib import Path

from commit_memory.memo_store import JsonStore
from commit_memory.memoService import MemoService
from commit_memory.validation import (
    ValidationError,
    validate_author,
    validate_file_path,
    validate_memo_text,
)

# We make sure that at the beginning of Pythons import is our assets
# so that we can import every file that is in the root directory

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_validation_functions():
    """Test the validation functions directly."""
    print("Testing validation functions...")

    # Test memo text validation
    print("\nTesting memo text validation:")
    try:
        # Valid memo
        result = validate_memo_text("This is a valid memo")
        print(f"Valid memo: {result}")

        # Empty memo
        try:
            validate_memo_text("")
            print("Empty memo validation failed - should have raised an error")
        except ValidationError as e:
            print(f"Empty memo correctly rejected: {e}")

        # Too long memo
        try:
            validate_memo_text("x" * 3000)  # Exceeds MAX_MEMO_LENGTH
            print("Long memo validation failed - should have raised an error")
        except ValidationError as e:
            print(f"Long memo correctly rejected: {e}")

        # Memo with HTML injection
        html_memo = "<script>alert('XSS')</script>"
        sanitized = validate_memo_text(html_memo)
        print(f"HTML memo sanitized: {sanitized}")
        if "<script>" in sanitized:
            print("HTML sanitization failed - script tag still present")
        else:
            print("HTML sanitization successful")

    except Exception as e:
        print(f"Unexpected error in memo validation: {e}")

    # Test author validation
    print("\nTesting author validation:")
    try:
        # Valid author
        result = validate_author("John Doe")
        print(f"Valid author: {result}")

        # Empty author
        try:
            validate_author("")
            print("Empty author validation failed - should have raised an error")
        except ValidationError as e:
            print(f"Empty author correctly rejected: {e}")

        # Too long author
        try:
            validate_author("x" * 150)  # Exceeds MAX_AUTHOR_LENGTH
            print("Long author validation failed - should have raised an error")
        except ValidationError as e:
            print(f"Long author correctly rejected: {e}")

    except Exception as e:
        print(f"Unexpected error in author validation: {e}")

    # Test file path validation
    print("\nTesting file path validation:")
    try:
        result = validate_file_path("src/main.py")
        print(f"Valid path: {result}")

        try:
            validate_file_path("")
            print("Empty path validation failed - should have raised an error")
        except ValidationError as e:
            print(f"Empty path correctly rejected: {e}")

        try:
            validate_file_path("../../../etc/passwd")
            print("Path traversal validation failed - should have raised an error")
        except ValidationError as e:
            print(f"Path traversal correctly rejected: {e}")

    except Exception as e:
        print(f"Unexpected error in path validation: {e}")


def test_memoservice_validation():
    """Test the integration of validation with MemoService."""
    print("\nTesting MemoService validation...")

    temp_store = JsonStore(Path("temp_test_store.json"))
    service = MemoService(temp_store)

    try:
        # Test add_commit_memo with a valid memo
        print("\nTesting add_commit_memo with valid memo:")
        try:
            commit = service.add_commit_memo("This is a valid memo")
            print(f"Valid memo added successfully to commit {commit}")
        except Exception as e:
            print(f"Error adding valid memo: {e}")

        # Test add_commit_memo with invalid memo (too long)
        print("\nTesting add_commit_memo with too long memo:")
        try:
            service.add_commit_memo("x" * 3000)  # Exceeds MAX_MEMO_LENGTH
            print("Long memo validation failed - should have raised an error")
        except ValidationError as e:
            print(f"Long memo correctly rejected: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        # Test update_memo with a valid memo
        print("\nTesting update_memo with valid memo:")
        try:
            commit_memos, _ = service.get_commit_memos(commit)
            if commit_memos:
                updated_memo = service.update_memo(commit, 0, "Updated memo text")
                print(f"Memo updated successfully: {updated_memo.memo}")
            else:
                print("No memos found to update")
        except Exception as e:
            print(f"Error updating memo: {e}")

        # Test update_memo with an invalid memo (too long)
        print("\nTesting update_memo with too long memo:")
        try:
            if commit_memos:
                service.update_memo(commit, 0, "x" * 3000)  # Exceeds MAX_MEMO_LENGTH
                print("Long memo validation failed - should have raised an error")
            else:
                print("No memos found to update")
        except ValidationError as e:
            print(f"Long memo correctly rejected: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        # Test search with a valid author
        print("\nTesting search with valid author:")
        try:
            memos = service.search("John")
            print(f"Search returned {len(memos)} memos")
        except Exception as e:
            print(f"Error searching for memos: {e}")

        # Test search with an invalid author (too long)
        print("\nTesting search with too long author:")
        try:
            service.search("x" * 150)  # Exceeds MAX_AUTHOR_LENGTH
            print("Long author validation failed - should have raised an error")
        except ValidationError as e:
            print(f"Long author correctly rejected: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    finally:
        if os.path.exists("temp_test_store.json"):
            os.remove("temp_test_store.json")
            print("\nTemporary test store removed")


if __name__ == "__main__":
    print("Running validation tests...")
    test_validation_functions()
    test_memoservice_validation()
    print("\nAll tests completed.")
