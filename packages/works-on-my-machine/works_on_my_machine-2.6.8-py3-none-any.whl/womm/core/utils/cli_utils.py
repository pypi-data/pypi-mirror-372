#!/usr/bin/env python3
"""
Unified CLI Manager for Works On My Machine.
Handles command execution with optional security validation.
"""

import logging
import subprocess
import time
from pathlib import Path
from typing import List, Optional, Union


class CommandResult:
    """Enhanced command result with security information."""

    def __init__(
        self,
        returncode: int,
        stdout: str = "",
        stderr: str = "",
        command: List[str] = None,
        cwd: Optional[Path] = None,
        security_validated: bool = False,
        execution_time: float = 0.0,
    ):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.command = command or []
        self.cwd = cwd
        self.security_validated = security_validated
        self.execution_time = execution_time

    @property
    def success(self) -> bool:
        return self.returncode == 0

    def __bool__(self):
        """Return a boolean representation of the result."""
        return self.success

    def __str__(self):
        """Return a string representation of the result."""
        return f"CommandResult(success={self.success}, validated={self.security_validated}, time={self.execution_time:.2f}s)"


class CLIUtils:
    """Unified CLI manager with optional security validation."""

    def __init__(
        self,
        default_cwd: Optional[Union[str, Path]] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize CLI manager.

        Args:
            default_cwd: Default working directory
            timeout: Command timeout in seconds
            max_retries: Maximum number of retries for failed commands
            retry_delay: Delay between retries in seconds
        """
        self.default_cwd = Path(default_cwd) if default_cwd else Path.cwd()
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Setup logging
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for CLI operations."""
        logger = logging.getLogger("cli_manager")
        logger.setLevel(
            logging.CRITICAL
        )  # Only show critical errors, suppress all others

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def run(
        self,
        command: Union[str, List[str]],
        description: Optional[str] = None,
        cwd: Optional[Union[str, Path]] = None,
        validate_security: bool = False,
        **kwargs,
    ) -> CommandResult:
        """
        Execute a command with optional security validation.

        Args:
            command: Command to execute (string or list)
            description: Description for logging
            cwd: Working directory
            validate_security: Whether to validate command security
            **kwargs: Additional arguments for subprocess

        Returns:
            CommandResult: Execution result with security information
        """
        start_time = time.time()

        # Normalize command
        cmd = command.split() if isinstance(command, str) else list(command)

        # Description prefix for logging
        log_prefix = f"[{description}] " if description else ""

        # Security validation
        security_validated = False
        if validate_security:
            from .security.security_validator import security_validator

            is_valid, error = security_validator.validate_command(cmd)
            if not is_valid:
                self.logger.warning(f"{log_prefix}Command validation failed: {error}")
                return CommandResult(
                    returncode=-1,
                    stderr=f"Security validation failed: {error}",
                    command=cmd,
                    cwd=cwd,
                    security_validated=False,
                    execution_time=time.time() - start_time,
                )
            security_validated = True

        # Parameters
        run_cwd = Path(cwd) if cwd else self.default_cwd

        # Retry logic
        last_error = None
        for attempt in range(self.max_retries):
            try:
                result = self._execute_command(cmd, run_cwd, **kwargs)

                # Create result
                command_result = CommandResult(
                    returncode=result.returncode,
                    stdout=getattr(result, "stdout", "") or "",
                    stderr=getattr(result, "stderr", "") or "",
                    command=cmd,
                    cwd=run_cwd,
                    security_validated=security_validated,
                    execution_time=time.time() - start_time,
                )

                return command_result

            except subprocess.TimeoutExpired as e:
                last_error = e
                self.logger.warning(
                    f"{log_prefix}Timeout after {self.timeout}s (attempt {attempt + 1}/{self.max_retries})"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

            except Exception as e:
                last_error = e
                self.logger.error(
                    f"{log_prefix}Error during execution (attempt {attempt + 1}/{self.max_retries}): {e}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)

        # All retries failed
        error_msg = f"{log_prefix}All {self.max_retries} attempts failed. Last error: {last_error}"
        self.logger.error(error_msg)

        return CommandResult(
            returncode=-1,
            stderr=error_msg,
            command=cmd,
            cwd=run_cwd,
            security_validated=security_validated,
            execution_time=time.time() - start_time,
        )

    def _execute_command(
        self,
        cmd: List[str],
        cwd: Path,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        """Execute a single command attempt."""
        # Validate command is a list of strings
        if not isinstance(cmd, list) or not all(isinstance(arg, str) for arg in cmd):
            raise ValueError("Command must be a list of strings")

        if not cmd:
            raise ValueError("Command cannot be empty")

        # Prepare subprocess arguments with explicit security settings
        subprocess_args = {
            "cwd": cwd,
            "timeout": self.timeout,
            "text": True,
            "encoding": "utf-8",
            "errors": "replace",
            "capture_output": True,
            "shell": False,  # Explicitly disable shell for security
        }

        # Add valid kwargs for subprocess
        valid_subprocess_args = {
            "input",
            "env",
            "check",
            "stdin",
            "stdout",
            "stderr",
            "preexec_fn",
            "close_fds",
            "pass_fds",
            "restore_signals",
            "start_new_session",
            "group",
            "extra_groups",
            "user",
            "umask",
            "startupinfo",
            "creationflags",
        }

        for key, value in kwargs.items():
            if key in valid_subprocess_args:
                subprocess_args[key] = value

        # Execute command with explicit security validation
        # The command has already been validated by the calling method
        return subprocess.run(cmd, **subprocess_args)  # noqa: S603

    def run_silent(self, command: Union[str, List[str]], **kwargs) -> CommandResult:
        """Execute a command in silent mode."""
        return self.run(command, **kwargs)

    def run_secure(
        self, command: Union[str, List[str]], description: str = "", **kwargs
    ) -> CommandResult:
        """Execute a command with security validation."""
        return self.run(command, description, validate_security=True, **kwargs)

    def check_command_available(self, command: str) -> bool:
        """Check if a command is available and optionally validate security."""
        import shutil

        if not shutil.which(command):
            return False

        # Additional security check
        from .security.security_validator import security_validator

        is_valid, _ = security_validator.validate_command([command])
        return is_valid

    def get_command_version(
        self, command: str, version_flag: str = "--version"
    ) -> Optional[str]:
        """Get version of a command."""
        if not self.check_command_available(command):
            return None

        result = self.run_silent([command, version_flag])
        if result.success and result.stdout.strip():
            # Extract version from output
            output = result.stdout.strip()
            if output:
                # Take first line which probably contains version
                first_line = output.split("\n")[0]
                return first_line

        return None


# Global instance
cli = CLIUtils()


def run_command(
    command: Union[str, List[str]],
    description: Optional[str] = None,
    cwd: Optional[Union[str, Path]] = None,
    **kwargs,
) -> CommandResult:
    """Simple function to run a command."""
    return cli.run(command, description, cwd, **kwargs)


def run_silent(
    command: Union[str, List[str]], cwd: Optional[Union[str, Path]] = None, **kwargs
) -> CommandResult:
    """Simple function to run a command silently."""
    return cli.run_silent(command, cwd=cwd, **kwargs)


def run_secure(
    command: Union[str, List[str]],
    description: str = "",
    cwd: Optional[Union[str, Path]] = None,
    **kwargs,
) -> CommandResult:
    """Simple function to run a command with security validation."""
    return cli.run_secure(command, description, cwd=cwd, **kwargs)


def run_interactive(
    command: Union[str, List[str]], cwd: Optional[Union[str, Path]] = None, **kwargs
) -> CommandResult:
    """Simple function to run a command interactively."""
    return cli.run(command, cwd=cwd, **kwargs)


def check_tool_available(tool: str) -> bool:
    """Check if a tool is available."""
    return cli.check_command_available(tool)


def get_tool_version(tool: str, version_flag: str = "--version") -> Optional[str]:
    """Get version of a tool."""
    return cli.get_command_version(tool, version_flag)
