import os
import subprocess
import sys
from pathlib import Path


def run_cli(args, cwd: Path | None = None):
    env = os.environ.copy()
    src = Path(__file__).resolve().parents[1] / 'src'
    env['PYTHONPATH'] = str(src)
    return subprocess.run(
        [sys.executable, '-m', 'quantumscan.cli', *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd) if cwd else None,
    )


def test_help_via_subprocess():
    result = run_cli(['--help'])
    assert result.returncode == 0
    assert 'usage' in result.stdout.lower()


def test_version_subprocess():
    result = run_cli(['--version'])
    assert result.returncode == 0
    assert 'quantumscan v0.1.0' in result.stdout


def test_no_findings_outputs_nothing(tmp_path: Path):
    empty = tmp_path / 'empty.py'
    empty.write_text('# no vuln')
    result = run_cli(['--path', str(tmp_path)])
    assert result.returncode == 0
    assert result.stdout.strip() == ''


def test_invalid_path_returns_error(tmp_path: Path):
    missing = tmp_path / 'nope'
    result = run_cli(['--path', str(missing)])
    assert result.returncode == 2


def test_edge_special_path(tmp_path: Path):
    special = tmp_path / '테스트경로'
    special.mkdir()
    result = run_cli(['--path', str(special)])
    assert result.returncode == 0


def test_max_file_mb_option(tmp_path: Path):
    big = tmp_path / 'big.py'
    big.write_text('a')
    result = run_cli(['--path', str(tmp_path), '--max-file-mb', '0'])
    assert result.returncode == 0
    assert 'WARN SKIPPED_LARGE_FILE' in result.stderr


def test_fail_on_findings_exits_nonzero(tmp_path: Path):
    (tmp_path / 'a.py').write_text('RSA.generate(2048)')
    result = run_cli(['--path', str(tmp_path), '--fail-on-findings', 'true'])
    assert result.returncode == 1


def test_exclude_skips_dir(tmp_path: Path):
    skipped = tmp_path / 'skip'
    skipped.mkdir()
    (skipped / 'a.py').write_text('md5')
    result = run_cli(['--path', str(tmp_path), '--exclude', str(skipped)])
    assert result.returncode == 0
    assert result.stdout.strip() == ''
