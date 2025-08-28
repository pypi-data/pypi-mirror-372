"""Tests for ListPromptResponse."""

from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_prompt_response_test import (
    AbstractPromptResponseTest,
)


class TestListPromptResponse(AbstractPromptResponseTest):
    """Test cases for ListPromptResponse."""

    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.data.list_prompt_response import (
            ListPromptResponse,
        )

        return ListPromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        kwargs = kwargs or {}
        kwargs.setdefault("items", [self._test_message])
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # List should show bullet points
        self._assert_contains_text(rendered, "•")

    def get_expected_lines(self) -> int:
        return 1  # Single list item

    def test_empty_list(self) -> None:
        response = self._create_test_response(items=[])
        rendered = response.render()
        assert rendered.strip() == ""

    def test_simple_list(self) -> None:
        items = ["First", "Second", "Third"]
        response = self._create_test_response(items=items)
        rendered = response.render()
        for item in items:
            self._assert_contains_text(rendered, item)

    def test_nested_list(self) -> None:
        items = [
            "Root item",
            "  • Sub item 1",
            "  • Sub item 2",
        ]
        response = self._create_test_response(items=items)
        rendered = response.render()
        for item in items:
            self._assert_contains_text(rendered, item.strip())

    def test_custom_bullet(self) -> None:
        bullet = "-"
        items = ["First", "Second", "Third"]
        response = self._create_test_response(items=items, bullet=bullet)
        rendered = response.render()
        for item in items:
            self._assert_contains_text(rendered, f"{bullet} {item}")

    def test_mixed_indentation(self) -> None:
        items = [
            "Level 0",
            "  Level 1",
            "    Level 2",
            "Level 0 again",
        ]
        response = self._create_test_response(items=items)
        rendered = response.render()
        lines = rendered.strip().split("\n")
        assert lines[0].startswith("• Level 0")
        assert lines[1].startswith("  • Level 1")
        assert lines[2].startswith("    • Level 2")
        assert lines[3].startswith("• Level 0")

    def test_custom_color(self) -> None:
        from wexample_prompt.enums.terminal_color import TerminalColor

        response = self._create_test_response(
            items=[self._test_message],
            color=TerminalColor.GREEN,
        )
        rendered = response.render()
        self._assert_contains_text(rendered, self._test_message)
        self._assert_contains_text(rendered, "\u001b[32m")
