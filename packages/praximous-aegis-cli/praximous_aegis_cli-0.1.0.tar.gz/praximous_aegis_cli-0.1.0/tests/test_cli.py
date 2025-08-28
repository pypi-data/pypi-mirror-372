import pytest
from click.testing import CliRunner
from pathlib import Path
from aegis_cli.cli import cli
from aegis_cli import detectors

def test_cli_help():
    """Test that CLI shows help"""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Automate security documentation' in result.output

def test_cli_no_args_detects_current_dir(mock_templates):
    """Test CLI with no arguments uses current directory"""
    runner = CliRunner()
    # Use an isolated filesystem to ensure the CWD is a predictable temp directory
    with runner.isolated_filesystem() as td:
        (Path(td) / 'requirements.txt').touch()
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert "Security files generated successfully" in result.output

def test_cli_dry_run(js_project, monkeypatch):
    """Test dry run functionality"""
    runner = CliRunner()
    
    monkeypatch.setattr(detectors, 'detect_language', lambda *args: 'javascript')
    
    result = runner.invoke(cli, [str(js_project), '--dry-run'])
    assert result.exit_code == 0
    assert 'Dry run' in result.output
    assert 'SECURITY.md' in result.output

def test_cli_verbose(js_project, monkeypatch):
    """Test verbose output"""
    runner = CliRunner()
    
    monkeypatch.setattr(detectors, 'detect_language', lambda *args: 'javascript')
    
    result = runner.invoke(cli, [str(js_project), '--verbose', '--dry-run'])
    assert result.exit_code == 0
    assert 'Scanning project' in result.output
    assert 'Detected language' in result.output

def test_cli_custom_output_dir(js_project, monkeypatch):
    """Test custom output directory"""
    runner = CliRunner()
    
    monkeypatch.setattr(detectors, 'detect_language', lambda *args: 'javascript')
    
    custom_dir = js_project / 'custom-security'
    result = runner.invoke(cli, [str(js_project), '--output', str(custom_dir), '--dry-run'])
    assert result.exit_code == 0
    assert str(custom_dir) in result.output

def test_cli_no_language_detected(empty_project):
    """Test behavior when no language is detected"""
    runner = CliRunner()
    result = runner.invoke(cli, [str(empty_project)])
    assert result.exit_code == 1
    assert 'Could not detect supported language' in result.output