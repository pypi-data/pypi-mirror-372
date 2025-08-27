"""Tests for main CLI functionality."""

import pytest
from typer.testing import CliRunner

from konecty_cli.main import app


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


def test_version_command(runner):
    """Test the version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "konecty-cli version 0.1.0" in result.stdout


def test_hello_command_default(runner):
    """Test the hello command with default values."""
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.stdout


def test_hello_command_with_name(runner):
    """Test the hello command with custom name."""
    result = runner.invoke(app, ["hello", "--name", "Alice"])
    assert result.exit_code == 0
    assert "Hello, Alice!" in result.stdout


def test_hello_command_with_count(runner):
    """Test the hello command with count."""
    result = runner.invoke(app, ["hello", "--count", "3"])
    assert result.exit_code == 0
    # Should appear 3 times
    assert result.stdout.count("Hello, World!") == 3


def test_info_command(runner):
    """Test the info command."""
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "Konecty CLI" in result.stdout
    assert "Version: 0.1.0" in result.stdout


def test_help_command(runner):
    """Test the help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Konecty CLI utilities" in result.stdout
    assert "version" in result.stdout
    assert "hello" in result.stdout
    assert "info" in result.stdout
