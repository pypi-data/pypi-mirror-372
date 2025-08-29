"""Tests for the cli commands."""
import pytest
from click import testing as ctest

from cau.cau_cli import cau_cli

@pytest.mark.usefixtures("mock_conan", "mock_project")
class TestRestore:
    """Tests for restore command."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures."""
        self.runner = ctest.CliRunner()

    def test_default_restore(self) -> None:
        """Asserts default restore correctly executes."""
        result = self.runner.invoke(cau_cli, ["restore"])
        assert result.exit_code == 0
        assert "Restored Conan" in result.output

@pytest.mark.usefixtures("mock_conan", "mock_git", "mock_tidy", "mock_project")
class TestLint:
    """Tests for lint command."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures."""
        self.runner = ctest.CliRunner()

    def test_default_lint(self) -> None:
        """Asserts default lint correctly executes."""
        result = self.runner.invoke(cau_cli, ["lint"])
        assert result.exit_code == 0
        assert "Restored Conan" in result.output
        assert "Got changes from git" in result.output
        assert "Lint was successful" in result.output

    def test_skip_conan_restore(self) -> None:
        """Asserts lint with skip restore correctly executes."""
        result = self.runner.invoke(cau_cli, ["lint", "--skip-restore"])
        assert result.exit_code == 0
        assert "Restored Conan" not in result.output
        assert "Got changes from git" in result.output
        assert "Lint was successful" in result.output

    def test_force_all_lint(self) -> None:
        """Asserts lint will force all files to be linted."""
        result = self.runner.invoke(cau_cli, ["lint", "--force"])
        assert result.exit_code == 0
        assert "Got all files" in result.output
        assert "Lint was successful" in result.output

@pytest.mark.usefixtures("mock_conan", "mock_project")
class TestBuild:
    """Tests for build command."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures."""
        self.runner = ctest.CliRunner()

    def test_default_build(self) -> None:
        """Asserts default build correctly execute."""
        result = self.runner.invoke(cau_cli, ["build"])
        assert result.exit_code == 0
        assert "Restored Conan" in result.output
        assert "Build successful" in result.output

    def test_skip_conan_restore(self) -> None:
        """Asserts build with skip restore correctly executes."""
        result = self.runner.invoke(cau_cli, ["build", "--skip-restore"])
        assert result.exit_code == 0
        assert "Restored Conan" not in result.output
        assert "Build successful" in result.output

@pytest.mark.usefixtures("mock_conan", "mock_project")
class TestClean:
    """Tests for clean command."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures."""
        self.runner = ctest.CliRunner()

    def test_clean_all_files(self) -> None:
        """Asserts clean all files correctly executes."""
        result = self.runner.invoke(cau_cli, ["clean", "--all-files"])
        assert result.exit_code == 0
        assert "Cleaned out build directory" in result.output
        assert "Cleaned out conan directory" in result.output

    def test_clean_build(self) -> None:
        """Asserts clean build correctly executes and only cleans build directory."""
        result = self.runner.invoke(cau_cli, ["clean", "--only-build"])
        assert result.exit_code == 0
        assert "Cleaned out build directory" in result.output
        assert "Cleaned out conan directory" not in result.output

    def test_clean_conan_files(self) -> None:
        """Asserts clean conan correctly executes and only cleans conan directory."""
        result = self.runner.invoke(cau_cli, ["clean", "--only-conan"])
        assert result.exit_code == 0
        assert "Cleaned out build directory" not in result.output
        assert "Cleaned out conan directory" in result.output

    def test_no_op(self) -> None:
        """Asserts nothing is done if not provided arguments."""
        result = self.runner.invoke(cau_cli, ["clean"])
        assert result.exit_code == 0
        assert "Cleaned out build directory" not in result.output
        assert "Cleaned out conan directory" not in result.output

@pytest.mark.usefixtures("mock_coverage", "mock_project")
class TestCoverage:
    """Tests for coverage command."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures."""
        self.runner = ctest.CliRunner()

    def test_default_coverage(self) -> None:
        """Asserts default coverage command runs coverage properly."""
        result = self.runner.invoke(cau_cli, [
            "coverage",
        ])
        assert result.exit_code == 0
        assert "Running coverage" in result.output

@pytest.mark.usefixtures("mock_valgrind", "mock_project")
class TestValgrind:
    """Tests for Valgrind commands."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures."""
        self.runner = ctest.CliRunner()

    def test_leak_check(self) -> None:
        """Asserts that leak_check command runs check properly."""
        result = self.runner.invoke(cau_cli, ["leak-check", "--project", "AProject"])
        assert result.exit_code == 0
        assert "Running memory check" in result.output

@pytest.mark.usefixtures("mock_project")
class TestGenerate:
    """Tests for generate command."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures."""
        self.runner = ctest.CliRunner()

    def test_generate_files(self) -> None:
        """Asserts files are generated correctly."""
        result = self.runner.invoke(cau_cli, ["generate", "AClass"])
        assert result.exit_code == 0
        assert "Generating AClass" in result.output

@pytest.mark.usefixtures("mock_project")
class TestNewModule:
    """Tests for new-module command."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures."""
        self.runner = ctest.CliRunner()

    def test_new_module(self) -> None:
        """Asserts new module is generated."""
        result = self.runner.invoke(cau_cli, ["new-module", "module", "submodule"])
        assert result.exit_code == 0
        assert "Creating new module" in result.output

@pytest.mark.usefixtures("mock_project")
class TestInitialize:
    """Tests for initialize command."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures."""
        self.runner = ctest.CliRunner()

    def test_initialize(self) -> None:
        """Asserts project is generated."""
        result = self.runner.invoke(cau_cli, ["initialize"])
        assert result.exit_code == 0
        assert "Initializing new project" in result.output

@pytest.mark.usefixtures("mock_project")
class TestNewConfig:
    """Tests for new-config command."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures."""
        self.runner = ctest.CliRunner()

    def test_new_config(self) -> None:
        """Asserts new configuration file is generated."""
        result = self.runner.invoke(cau_cli, ["new-config"])
        assert result.exit_code == 0
        assert "Creating default cauproject.toml file." in result.output
