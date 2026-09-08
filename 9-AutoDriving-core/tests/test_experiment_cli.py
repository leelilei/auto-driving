"""Integration tests for unified experiment CLI subcommands."""

import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/experiment.py"
PYTHON = sys.executable


def run_cli(*args):
    cmd = [PYTHON, str(CLI)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))


def test_cli_help():
    res = run_cli("--help")
    assert res.returncode == 0
    assert "preflight" in res.stdout
    assert "validate-data" in res.stdout
    assert "replay" in res.stdout


def test_cli_preflight():
    res = run_cli("preflight")
    assert res.returncode == 0
    assert "Preflight status: PASS" in res.stdout


def test_cli_validate_data():
    res = run_cli("validate-data")
    assert res.returncode == 0
    assert "Data validation result: PASS" in res.stdout


def test_cli_collect_dry_run():
    res = run_cli("collect", "--split", "pilot", "--dry-run")
    assert res.returncode == 0
    assert "[DRY RUN MODE]" in res.stdout


def test_cli_collect_blocked_without_verification():
    res = run_cli("collect", "--split", "pilot")
    # Must exit with non-zero (code 2) because annotation is pending
    assert res.returncode != 0
    assert "[BLOCKED]" in res.stdout


def test_cli_offline_replay():
    res = run_cli("replay", "--limit", "4")
    assert res.returncode == 0
    assert "Baseline C01 verified" in res.stdout
