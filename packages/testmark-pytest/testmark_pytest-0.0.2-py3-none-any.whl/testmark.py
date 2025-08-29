from __future__ import annotations

import inspect
import json
import re
import shutil
import subprocess
import sys
from typing import Callable, Dict, Any, List


def testmark(test_file: str, fn: Callable[[str], str]) -> None:
    """
    Generate pytest tests from a .test.md file for a given string->string function.

    Usage:
        from testmark import testmark
        from mypkg import slugify
        testmark('examples/slugify.test.md', slugify)
    """
    # Parse test cases via Node CLI (single file)
    result = _run_cli([test_file])
    tests: List[Dict[str, Any]] = result["tests"]

    # Dynamically create test functions in the caller's module
    caller_frame = inspect.currentframe().f_back  # type: ignore[assignment]
    assert caller_frame is not None
    mod_globals = caller_frame.f_globals

    used_names = set()
    for i, case in enumerate(tests):
        base = _slugify(case.get("name", f"case_{i}"))
        name = f"test_{base}"
        suffix = 2
        while name in used_names or name in mod_globals:
            name = f"test_{base}_{suffix}"
            suffix += 1
        used_names.add(name)

        def _make(case: Dict[str, Any]):
            def _test():
                try:
                    import pytest  # Local import so module can be imported without pytest installed
                except Exception as exc:  # pragma: no cover
                    raise RuntimeError("pytest is required to run TestMark adapter") from exc

                if case.get("error") is not None:
                    with pytest.raises(Exception, match=re.escape(case["error"])):
                        fn(case.get("input", ""))
                else:
                    assert fn(case.get("input", "")) == case.get("output", "")

            _test.__doc__ = case.get("name", name)
            return _test

        mod_globals[name] = _make(case)


def _resolve_cli() -> str:
    """Return the testmark executable path from PATH, or raise with a helpful message."""
    bin_path = shutil.which("testmark")
    if not bin_path:
        raise RuntimeError(
            "testmark CLI not found on PATH. Install it globally with `npm i -g testmark`."
        )
    return bin_path


def _run_cli(files: List[str]) -> Dict[str, Any]:
    """Run testmark CLI on a single file and return parsed JSON object."""
    if not files or len(files) != 1:
        raise ValueError("_run_cli expects exactly one file path")
    cmd = [_resolve_cli(), files[0]]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise RuntimeError(f"testmark CLI failed with exit code {proc.returncode}")
    data = json.loads(proc.stdout)
    if not isinstance(data, dict) or "tests" not in data:
        raise RuntimeError("Unexpected testmark CLI output shape")
    return data


def _slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "case"


__all__ = ["testmark"]
