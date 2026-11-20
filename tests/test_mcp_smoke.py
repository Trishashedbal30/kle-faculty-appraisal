import asyncio
import argparse
import tempfile
from pathlib import Path

from app.mcp_client import probe
from app.mcp_server import _loopback_host, _resolve_store
from app.store import Store


def test_mcp_sse_bind_is_limited_to_loopback():
    assert _loopback_host('127.0.0.1') == '127.0.0.1'
    assert _loopback_host('::1') == '::1'
    for host in ('0.0.0.0', '::', '192.0.2.1', 'localhost'):
        try:
            _loopback_host(host)
        except argparse.ArgumentTypeError:
            continue
        raise AssertionError(f'Non-numeric or non-loopback MCP host was accepted: {host}')


def test_mcp_probe_returns_tools_with_timeout():
    from app.demo import make_fixture

    project_root = Path(__file__).resolve().parents[1]
    demo_dir = project_root / 'runtime-demo'
    demo_dir.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.mcp-test-', dir=demo_dir) as temporary_dir:
        demo_store = Store(Path(temporary_dir) / 'app.db')
        make_fixture(demo_store, ready=True)
        result = asyncio.run(probe(db_path=str(demo_store.path), timeout=30.0))
    expected = {
        'check_source_consent',
        'get_approved_policy',
        'get_faculty_profile',
        'list_activity_records',
        'search_evidence',
    }
    assert result['count'] == 5
    assert set(result['tools']) == expected


def test_mcp_database_is_confined_to_marked_synthetic_demo(tmp_path, monkeypatch):
    import app.mcp_server as mcp_server

    monkeypatch.setattr(mcp_server, 'PROJECT_ROOT', tmp_path)
    monkeypatch.setenv('APP_DB', str(tmp_path / 'runtime' / 'app.db'))

    try:
        _resolve_store(str(tmp_path / 'runtime' / 'app.db'))
    except ValueError as exc:
        assert 'inside runtime-demo' in str(exc)
    else:
        raise AssertionError('MCP accepted a database outside runtime-demo.')

    demo_db = tmp_path / 'runtime-demo' / 'app.db'
    Store(demo_db).put('meta', {
        'id': 'import',
        'notes': ['SYNTHETIC SANDBOX: test-only fixture'],
    })
    assert _resolve_store(str(demo_db)).path == demo_db

    empty_db = tmp_path / 'runtime-demo' / 'empty.db'
    try:
        _resolve_store(str(empty_db))
    except ValueError as exc:
        assert 'synthetic demo database' in str(exc)
    else:
        raise AssertionError('MCP accepted an unmarked database inside runtime-demo.')
