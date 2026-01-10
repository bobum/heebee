"""
Pytest configuration and fixtures for Heebee game tests.

This module provides utilities to extract and test Python code from Ren'Py .rpy files.
"""
import pytest
import re
import sys
from pathlib import Path

# Add game directory to path for imports
GAME_DIR = Path(__file__).parent.parent / "game"
sys.path.insert(0, str(GAME_DIR))


def extract_python_from_rpy(rpy_path: Path) -> str:
    """
    Extract Python code from a Ren'Py .rpy file.

    Extracts code from:
    - `init python:` blocks
    - `python:` blocks
    - Class and function definitions within those blocks
    """
    content = rpy_path.read_text()
    python_code = []

    # Track if we're in a python block and its indentation
    in_python_block = False
    block_indent = 0

    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check for python block start
        if stripped.startswith('init python:') or stripped == 'python:':
            in_python_block = True
            # Get the indentation of the python: line
            block_indent = len(line) - len(line.lstrip())
            i += 1
            continue

        if in_python_block:
            # Check if we've exited the block (line with same or less indentation that's not empty)
            current_indent = len(line) - len(line.lstrip()) if line.strip() else block_indent + 1

            if line.strip() and current_indent <= block_indent:
                in_python_block = False
            else:
                # Remove the block indentation and add to python code
                if line.strip():
                    # Remove base indentation (typically 4 spaces inside init python:)
                    dedent_amount = block_indent + 4
                    if len(line) >= dedent_amount:
                        python_code.append(line[dedent_amount:])
                    else:
                        python_code.append(line.lstrip())
                else:
                    python_code.append('')

        i += 1

    return '\n'.join(python_code)


def load_rpy_classes(rpy_path: Path, namespace: dict = None) -> dict:
    """
    Load Python classes from a Ren'Py file into a namespace.

    Returns a dictionary containing all defined classes and functions.
    """
    if namespace is None:
        namespace = {}

    # Add common imports that Ren'Py provides
    namespace['renpy'] = MockRenpy()
    namespace['persistent'] = MockPersistent()

    python_code = extract_python_from_rpy(rpy_path)

    try:
        exec(python_code, namespace)
    except Exception as e:
        raise RuntimeError(f"Failed to load {rpy_path}: {e}")

    return namespace


class MockRenpy:
    """Mock renpy module for testing outside of Ren'Py."""

    def __init__(self):
        self.random = __import__('random')

    def show_screen(self, *args, **kwargs):
        pass

    def hide_screen(self, *args, **kwargs):
        pass

    def notify(self, message):
        pass

    def call_in_new_context(self, *args, **kwargs):
        pass

    def restart_interaction(self):
        """Mock restart_interaction for combat system."""
        pass


class MockPersistent:
    """Mock persistent storage for testing."""

    def __getattr__(self, name):
        return None

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)


@pytest.fixture
def game_dir():
    """Return the game directory path."""
    return GAME_DIR


@pytest.fixture
def mock_renpy():
    """Provide a mock renpy module."""
    return MockRenpy()


@pytest.fixture
def load_system():
    """Factory fixture to load a game system from its .rpy file."""
    def _load(system_name: str) -> dict:
        rpy_path = GAME_DIR / f"{system_name}.rpy"
        if not rpy_path.exists():
            pytest.skip(f"{system_name}.rpy not found")
        return load_rpy_classes(rpy_path)
    return _load
