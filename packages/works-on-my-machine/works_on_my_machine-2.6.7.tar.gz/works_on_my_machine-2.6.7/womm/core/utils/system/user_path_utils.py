#!/usr/bin/env python3
"""
Utilities for PATH and registry operations (shared helpers).
"""

import os
from typing import Union


def extract_path_from_reg_output(output: Union[str, bytes]) -> str:
    """Extract PATH value from `reg query` output, supporting REG_SZ and REG_EXPAND_SZ.

    Args:
        output: Raw stdout from `reg query` command

    Returns:
        Extracted PATH value or empty string if not found
    """
    try:
        if isinstance(output, (bytes, bytearray)):
            output = output.decode("utf-8", errors="ignore")
        for line in str(output).splitlines():
            if "PATH" in line and ("REG_SZ" in line or "REG_EXPAND_SZ" in line):
                if "REG_EXPAND_SZ" in line:
                    parts = line.split("REG_EXPAND_SZ")
                else:
                    parts = line.split("REG_SZ")
                if len(parts) > 1:
                    return parts[1].strip()
    except Exception:
        return ""
    return ""


def deduplicate_path_entries(path_value: str) -> str:
    """Deduplicate PATH entries preserving first occurrence and order.

    Comparison is done case-insensitively on expanded values with trailing
    slashes/backslashes trimmed. The original first textual form is kept.
    """
    if not path_value:
        return path_value

    seen: set[str] = set()
    result_parts: list[str] = []
    for raw_part in path_value.split(";"):
        part = raw_part.strip()
        if not part:
            continue
        key = os.path.expandvars(part).rstrip("/\\").lower()
        if key in seen:
            continue
        seen.add(key)
        result_parts.append(part)
    return ";".join(result_parts)
