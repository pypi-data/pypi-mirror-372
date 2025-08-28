"""
Test suite for CLI commands
"""
import pytest
from typer.testing import CliRunner
from clyrdia.cli_modular import app

runner = CliRunner()

class TestCLICommands:
    """Test all CLI commands"""

    def test_help_command(self):
        """Test help command"""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout
        assert "run" in result.stdout
        assert "models" in result.stdout
        assert "cache" in result.stdout
        assert "dashboard" in result.stdout

    def test_run_command_help(self):
        """Test run command help"""
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout
        assert "--config" in result.stdout
        assert "--models" in result.stdout

    def test_models_command_help(self):
        """Test models command help"""
        result = runner.invoke(app, ["models", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout

    def test_cache_command_help(self):
        """Test cache command help"""
        result = runner.invoke(app, ["cache", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout
        assert "stats" in result.stdout
        assert "clear" in result.stdout

    def test_dashboard_command_help(self):
        """Test dashboard command help"""
        result = runner.invoke(app, ["dashboard", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout

    def test_credits_command_help(self):
        """Test credits command help"""
        result = runner.invoke(app, ["credits", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout

    def test_login_command_help(self):
        """Test login command help"""
        result = runner.invoke(app, ["login", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout

    def test_logout_command_help(self):
        """Test logout command help"""
        result = runner.invoke(app, ["logout", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout

    def test_env_command_help(self):
        """Test env command help"""
        result = runner.invoke(app, ["env", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout

    def test_run_command_missing_config(self):
        """Test run command without config file"""
        result = runner.invoke(app, ["run"])
        assert result.exit_code != 0
        assert "Missing option" in result.stdout

    def test_cache_stats_command(self):
        """Test cache stats command"""
        result = runner.invoke(app, ["cache", "stats"])
        assert result.exit_code == 0

    def test_cache_clear_command(self):
        """Test cache clear command"""
        result = runner.invoke(app, ["cache", "clear"])
        assert result.exit_code == 0

    def test_models_command(self):
        """Test models command"""
        result = runner.invoke(app, ["models"])
        assert result.exit_code == 0
        assert "Available Models" in result.stdout

    def test_env_command(self):
        """Test env command"""
        result = runner.invoke(app, ["env"])
        assert result.exit_code == 0
        assert "Environment Configuration" in result.stdout

    def test_credits_command(self):
        """Test credits command"""
        result = runner.invoke(app, ["credits"])
        assert result.exit_code == 0

    def test_login_command(self):
        """Test login command"""
        result = runner.invoke(app, ["login"])
        assert result.exit_code == 0

    def test_logout_command(self):
        """Test logout command"""
        result = runner.invoke(app, ["logout"])
        assert result.exit_code == 0

    def test_dashboard_command(self):
        """Test dashboard command"""
        result = runner.invoke(app, ["dashboard"])
        assert result.exit_code == 0

    def test_invalid_command(self):
        """Test invalid command"""
        result = runner.invoke(app, ["invalid-command"])
        assert result.exit_code != 0
        assert "No such command" in result.stdout

    def test_command_aliases(self):
        """Test command aliases work"""
        # Test short form of help
        result = runner.invoke(app, ["-h"])
        assert result.exit_code == 0
        assert "Usage:" in result.stdout

    def test_verbose_flag(self):
        """Test verbose flag on run command"""
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "--verbose" in result.stdout

    def test_no_cache_flag(self):
        """Test no-cache flag on run command"""
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "--no-cache" in result.stdout

    def test_output_flag(self):
        """Test output flag on run command"""
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "--output" in result.stdout
