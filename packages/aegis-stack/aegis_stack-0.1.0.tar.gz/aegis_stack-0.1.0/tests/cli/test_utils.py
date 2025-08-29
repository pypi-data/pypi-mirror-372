"""
Shared utilities for CLI testing.

This module provides common functionality used across all CLI test files
to avoid code duplication and ensure consistent behavior.
"""

from pathlib import Path
import subprocess
from typing import Any

import pytest

# Test Configuration Constants
CLI_TIMEOUT_QUICK = 10  # For fast help commands
CLI_TIMEOUT_STANDARD = 60  # For normal commands
CLI_TIMEOUT_LONG = 180  # For complex operations

QUALITY_CHECK_TIMEOUTS = {
    "dependency_install": 180,
    "cli_install": 60,
    "lint": 60,
    "typecheck": 120,
    "tests": 120,
}

STANDARD_ENV_OVERRIDES = {
    "VIRTUAL_ENV": "",  # Ensure clean uv environment
}


def find_project_root() -> Path:
    """Find the project root directory by looking for pyproject.toml."""
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / "pyproject.toml").exists() and (parent / "aegis").exists():
            return parent
    raise RuntimeError("Could not find project root directory")


PROJECT_ROOT = find_project_root()


class CLITestResult:
    """Container for CLI test results with enhanced validation support."""

    def __init__(
        self,
        returncode: int,
        stdout: str,
        stderr: str,
        project_path: Path | None = None,
        duration: float = 0.0,
        step: str = "",
    ):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.project_path = project_path
        self.success = returncode == 0
        self.duration = duration
        self.step = step
        self.error_message = "" if self.success else f"Exit code: {returncode}"

    def __str__(self) -> str:
        status = "✅" if self.success else "❌"
        return f"{status} {self.step or 'Command'} ({self.duration:.1f}s)"


def run_command(
    cmd: list[str],
    cwd: Path | None = None,
    timeout: int = 60,
    env_overrides: dict[str, str] | None = None,
    step_name: str = "Command",
    project_path: Path | None = None,
) -> CLITestResult:
    """
    Universal command runner for all test scenarios.

    Args:
        cmd: Command list to execute
        cwd: Working directory (defaults to PROJECT_ROOT)
        timeout: Command timeout in seconds
        env_overrides: Environment variable overrides
        step_name: Description of what this command does
        project_path: Associated project path for result

    Returns:
        CLITestResult with command results and timing
    """
    import os
    import time

    start_time = time.time()

    try:
        # Setup environment
        env = os.environ.copy()
        if env_overrides:
            env.update(env_overrides)

        # Default working directory
        if cwd is None:
            cwd = PROJECT_ROOT

        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )

        duration = time.time() - start_time
        return CLITestResult(
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            project_path=project_path,
            duration=duration,
            step=step_name,
        )

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return CLITestResult(
            returncode=1,
            stdout="",
            stderr=f"Command timed out after {timeout}s",
            project_path=project_path,
            duration=duration,
            step=step_name,
        )
    except FileNotFoundError as e:
        duration = time.time() - start_time
        if "uv" in str(e):
            return CLITestResult(
                returncode=1,
                stdout="",
                stderr=(
                    f"uv command not found. Please install uv or ensure it's in PATH. "
                    f"Error: {e}"
                ),
                project_path=project_path,
                duration=duration,
                step=step_name,
            )
        raise


def run_aegis_command(
    subcommand: str,
    *args: str,
    timeout: int | None = None,
    expect_success: bool = True,
    **kwargs: Any,
) -> CLITestResult:
    """
    Run an aegis CLI command and return results.

    Args:
        subcommand: The aegis subcommand (init, version, components)
        *args: Additional arguments to pass to the command
        timeout: Command timeout in seconds (defaults to CLI_TIMEOUT_STANDARD)
        expect_success: Whether to expect the command to succeed
        **kwargs: Additional keyword arguments (unused, for compatibility)

    Returns:
        CLITestResult with command results
    """
    if timeout is None:
        timeout = CLI_TIMEOUT_STANDARD

    cmd = ["uv", "run", "python", "-m", "aegis", subcommand] + list(args)

    return run_command(
        cmd=cmd,
        timeout=timeout,
        step_name=f"aegis {subcommand}",
    )


def run_project_command(
    cmd: list[str],
    project_path: Path,
    timeout: int | None = None,
    step_name: str = "Project Command",
    env_overrides: dict[str, str] | None = None,
) -> CLITestResult:
    """
    Run a command in a generated project directory.

    Args:
        cmd: Command list to execute
        project_path: Path to the generated project
        timeout: Command timeout in seconds (defaults to CLI_TIMEOUT_STANDARD)
        step_name: Description of what this command does
        env_overrides: Environment variable overrides (defaults to
            STANDARD_ENV_OVERRIDES)

    Returns:
        CLITestResult with command results
    """
    if timeout is None:
        timeout = CLI_TIMEOUT_STANDARD

    if env_overrides is None:
        env_overrides = STANDARD_ENV_OVERRIDES.copy()

    return run_command(
        cmd=cmd,
        cwd=project_path,
        timeout=timeout,
        step_name=step_name,
        project_path=project_path,
        env_overrides=env_overrides,
    )


def run_quality_checks(project_path: Path, timeout: int = 120) -> list[CLITestResult]:
    """
    Run standard quality checks on a generated project.

    Args:
        project_path: Path to the generated project
        timeout: Timeout for each command (used as fallback)

    Returns:
        List of CLITestResult for each quality check
    """
    results = []

    # Install dependencies
    results.append(
        run_project_command(
            ["uv", "sync", "--extra", "dev"],
            project_path,
            timeout=QUALITY_CHECK_TIMEOUTS["dependency_install"],
            step_name="Dependency Installation",
            env_overrides=STANDARD_ENV_OVERRIDES,
        )
    )

    # CLI installation
    results.append(
        run_project_command(
            ["uv", "pip", "install", "-e", "."],
            project_path,
            timeout=QUALITY_CHECK_TIMEOUTS["cli_install"],
            step_name="CLI Installation",
            env_overrides=STANDARD_ENV_OVERRIDES,
        )
    )

    # Linting with fixes
    results.append(
        run_project_command(
            ["uv", "run", "ruff", "check", "--fix", "."],
            project_path,
            timeout=QUALITY_CHECK_TIMEOUTS["lint"],
            step_name="Linting",
            env_overrides=STANDARD_ENV_OVERRIDES,
        )
    )

    # Type checking
    results.append(
        run_project_command(
            ["uv", "run", "mypy", "."],
            project_path,
            timeout=QUALITY_CHECK_TIMEOUTS["typecheck"],
            step_name="Type Checking",
            env_overrides=STANDARD_ENV_OVERRIDES,
        )
    )

    # Tests
    results.append(
        run_project_command(
            ["uv", "run", "pytest", "-v"],
            project_path,
            timeout=QUALITY_CHECK_TIMEOUTS["tests"],
            step_name="Tests",
            env_overrides=STANDARD_ENV_OVERRIDES,
        )
    )

    return results


def run_aegis_init(
    project_name: str,
    components: list[str] | None = None,
    output_dir: Path | None = None,
    interactive: bool = False,
    force: bool = True,
    yes: bool = True,
    timeout: int | None = None,
) -> CLITestResult:
    """
    Run the aegis init command and return results.

    Args:
        project_name: Name of the project to create
        components: List of components to include
        output_dir: Directory to create project in
        interactive: Whether to use interactive mode
        force: Whether to force overwrite
        yes: Whether to skip confirmation
        timeout: Command timeout in seconds (defaults to CLI_TIMEOUT_STANDARD)

    Returns:
        CLITestResult with command results and project path
    """
    if timeout is None:
        timeout = CLI_TIMEOUT_STANDARD

    args = [project_name]

    if components:
        args.extend(["--components", ",".join(components)])
    if output_dir:
        args.extend(["--output-dir", str(output_dir)])
    if not interactive:
        args.append("--no-interactive")
    if force:
        args.append("--force")
    if yes:
        args.append("--yes")

    result = run_aegis_command("init", *args, timeout=timeout)

    # Set the project path for init commands
    # Account for project name slug conversion (underscores to hyphens)
    project_slug = project_name.lower().replace(" ", "-").replace("_", "-")
    if output_dir:
        result.project_path = output_dir / project_slug
    else:
        result.project_path = PROJECT_ROOT / project_slug

    return result


def validate_project_structure(
    project_path: Path, expected_files: list[str]
) -> list[str]:
    """Validate that expected files/directories exist in generated project."""
    missing_files = []

    for expected_file in expected_files:
        file_path = project_path / expected_file
        if not file_path.exists():
            missing_files.append(expected_file)

    return missing_files


def validate_docker_compose(
    project_path: Path, expected_services: list[str]
) -> list[str]:
    """Validate Docker Compose services are correctly defined."""
    docker_compose_path = project_path / "docker-compose.yml"

    if not docker_compose_path.exists():
        return ["docker-compose.yml file missing"]

    try:
        content = docker_compose_path.read_text()
        missing_services = []

        for service in expected_services:
            if f"{service}:" not in content:
                missing_services.append(
                    f"Service '{service}' not found in docker-compose.yml"
                )

        return missing_services

    except Exception as e:
        return [f"Error reading docker-compose.yml: {e}"]


def validate_pyproject_dependencies(
    project_path: Path, expected_deps: list[str]
) -> list[str]:
    """Validate that required dependencies are in pyproject.toml."""
    pyproject_path = project_path / "pyproject.toml"

    if not pyproject_path.exists():
        return ["pyproject.toml file missing"]

    try:
        content = pyproject_path.read_text()
        missing_deps = []

        for dep in expected_deps:
            # Check for dependency with or without version constraints
            if f'"{dep}' not in content and f"'{dep}" not in content:
                missing_deps.append(f"Dependency '{dep}' not found in pyproject.toml")

        return missing_deps

    except Exception as e:
        return [f"Error reading pyproject.toml: {e}"]


def assert_file_exists(project_path: Path, relative_path: str) -> None:
    """Assert that a file exists in the generated project."""
    file_path = project_path / relative_path
    assert file_path.exists(), f"Expected file not found: {relative_path}"


def assert_file_contains(project_path: Path, relative_path: str, content: str) -> None:
    """Assert that a file contains specific content."""
    file_path = project_path / relative_path
    assert file_path.exists(), f"File not found: {relative_path}"

    file_content = file_path.read_text()
    assert content in file_content, f"Content '{content}' not found in {relative_path}"


def assert_database_config_present(config_content: str) -> None:
    """Assert that database configuration is present in config content."""
    assert "DATABASE_URL" in config_content
    assert "sqlite:///./data/app.db" in config_content
    assert "DATABASE_ENGINE_ECHO" in config_content
    assert "DATABASE_CONNECT_ARGS" in config_content
    assert "check_same_thread" in config_content


def assert_database_config_absent(config_content: str) -> None:
    """Assert that database configuration is absent from config content."""
    assert "DATABASE_URL" not in config_content
    assert "DATABASE_ENGINE_ECHO" not in config_content
    assert "DATABASE_CONNECT_ARGS" not in config_content


def assert_db_file_uses_settings(db_content: str) -> None:
    """Assert that db.py properly uses settings."""
    assert "from app.core.config import settings" in db_content
    assert "settings.DATABASE_URL" in db_content
    assert "settings.DATABASE_CONNECT_ARGS" in db_content
    assert "settings.DATABASE_ENGINE_ECHO" in db_content


def assert_db_file_structure(db_content: str) -> None:
    """Assert that db.py has complete structure including session management."""
    # First check basic settings usage
    assert_db_file_uses_settings(db_content)

    # Check imports
    assert "from contextlib import contextmanager" in db_content
    assert "from sqlalchemy import create_engine, event" in db_content
    assert "from sqlalchemy.orm import sessionmaker" in db_content
    assert "from sqlmodel import Session" in db_content

    # Check engine creation
    assert "engine = create_engine(" in db_content

    # Check foreign key pragma
    assert '@event.listens_for(engine, "connect")' in db_content
    assert "PRAGMA foreign_keys=ON" in db_content

    # Check SessionLocal factory
    assert "SessionLocal = sessionmaker(" in db_content
    assert "class_=Session" in db_content
    assert "autoflush=False" in db_content
    assert "autocommit=False" in db_content

    # Check context manager
    assert "@contextmanager" in db_content
    assert "def db_session(autocommit: bool = True)" in db_content
    assert "db_session.commit()" in db_content
    assert "db_session.rollback()" in db_content
    assert "db_session.close()" in db_content


def run_cli_help_command(*args: str, timeout: int | None = None) -> CLITestResult:
    """
    Run CLI help commands with shorter timeout for quick tests.

    Args:
        *args: Arguments to pass to aegis command
        timeout: Command timeout in seconds (defaults to CLI_TIMEOUT_QUICK)

    Returns:
        CLITestResult with command results
    """
    if timeout is None:
        timeout = CLI_TIMEOUT_QUICK

    cmd = ["uv", "run", "python", "-m", "aegis"] + list(args)
    return run_command(
        cmd=cmd,
        timeout=timeout,
        step_name=f"aegis {' '.join(args)}",
    )


def run_aegis_init_expect_failure(
    project_name: str,
    components: list[str],
    output_dir: Path,
    timeout: int = 30,
) -> CLITestResult:
    """Run aegis init command expecting it to fail."""
    result = run_aegis_init(project_name, components, output_dir, timeout=timeout)

    # For error testing, we expect failures
    assert not result.success, (
        f"Expected command to fail but it succeeded\n"
        f"Project: {project_name}\n"
        f"Components: {components}\n"
        f"STDOUT: {result.stdout}\n"
        f"STDERR: {result.stderr}"
    )

    return result


def check_error_indicators(
    output: str, expected_indicators: list[str], description: str
) -> None:
    """Check that error output contains expected indicators."""
    output_lower = output.lower()
    missing_indicators = []

    for indicator in expected_indicators:
        if indicator.lower() not in output_lower:
            missing_indicators.append(indicator)

    if missing_indicators:
        # More flexible matching - at least one indicator should be present
        if len(missing_indicators) == len(expected_indicators):
            pytest.fail(
                f"Error message missing expected indicators for {description}\n"
                f"Expected any of: {expected_indicators}\n"
                f"Got output: {output}\n"
                f"Missing all indicators: {missing_indicators}"
            )
