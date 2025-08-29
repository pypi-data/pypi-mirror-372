"""Tests for a TidyMessage."""
import pathlib

import pytest

from cau.wrappers.Clang import TidyMessage

class TestTidyMessage:
    """Tests for a TidyMessage."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Setup of test fixtures and data."""
        self.data = (
            "include/units/property.hpp:36:9: error: function 'Value' should be marked "
            "[[nodiscard]] [modernize-use-nodiscard,-warnings-as-errors]\n"
            "   36 |         constexpr auto Value() const -> double { return this->value_; }\n"
            "      |         ^\n"
            "      |         [[nodiscard]]\n"
        )
        self.expected = TidyMessage(
            file_name=pathlib.Path("include/units/property.hpp"),
            line=36,
            column=9,
            level="error",
            diagnostic="function 'Value' should be marked [[nodiscard]]",
            checks="[modernize-use-nodiscard,-warnings-as-errors]",
            message=(
                "   36 |         constexpr auto Value() const -> double { return this->value_; }\n"
                "      |         ^\n"
                "      |         [[nodiscard]]\n"
            ),
        )
        self.result = None

    def test_that_message_is_correctly_parsed(self) -> None:
        """Asserts that a message is parsed correctly."""
        self.result = TidyMessage.parse(self.data)
        assert self.result == self.expected

    def test_that_message_to_string_creates_original_message(self) -> None:
        """Asserts that converting back to string gives the original message."""
        self.result = TidyMessage.parse(self.data)
        assert str(self.result) == self.data

    def test_hash_is_calculated(self) -> None:
        """Asserts that a hash is calculated."""
        assert hash(self.expected)

    def test_equality(self) -> None:
        """Asserts equality operator."""
        assert self.expected == self.expected

def test_tidy_messages_are_correctly_parsed() -> None:
    """Asserts that a clang tidy message is correctly parsed."""
    number_of_messages = 2
    raw_text = (
        b"include/units/property.hpp:36:9: error: function 'Value' should be marked "
        b"[[nodiscard]] [modernize-use-nodiscard,-warnings-as-errors]\n"
        b"   36 |         constexpr auto Value() const -> double { return this->value_; }\n"
        b"      |         ^\n"
        b"      |         [[nodiscard]]\n"
        b"include/units/property.hpp:53:36: error: function "
        b"'ValueAs<fluid_props::Dimensionless>' should be marked [[nodiscard]] "
        b"[modernize-use-nodiscard,-warnings-as-errors]\n"
        b"   53 |         template <typename ToUnit> constexpr auto ValueAs(const ToUnit &unit) const -> double\n"
        b"      |                                    ^\n"
        b"      |                                    [[nodiscard]]\n"
    )
    result = TidyMessage.parse_all(raw_text)
    assert len(result) == number_of_messages
