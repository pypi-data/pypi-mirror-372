"""Tests for SuggestionsPromptResponse."""

from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_prompt_response_test import (
    AbstractPromptResponseTest,
)


class TestSuggestionsPromptResponse(AbstractPromptResponseTest):
    """Test cases for SuggestionsPromptResponse."""

    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.data.suggestions_prompt_response import (
            SuggestionsPromptResponse,
        )

        return SuggestionsPromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        kwargs = kwargs or {}
        kwargs.setdefault("message", self._test_message)
        kwargs.setdefault(
            "suggestions", ["command1 --arg value", "command2", "command3 --flag"]
        )
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # Should include arrow indicators
        self._assert_contains_text(rendered, "→")

    def get_expected_lines(self) -> int:
        # Empty lines (2) + message (1) + 3 suggestions
        return 6

    def test_render_with_single_suggestion(self) -> None:
        response = self._create_test_response(
            message=self._test_message,
            suggestions=["command1 --arg value"],
        )
        rendered = response.render()
        self._assert_contains_text(rendered, self._test_message)
        self._assert_contains_text(rendered, "command1 --arg value")

    def test_render_with_empty_suggestions(self) -> None:
        response = self._create_test_response(
            message=self._test_message,
            suggestions=[],
        )
        rendered = response.render()
        self._assert_contains_text(rendered, self._test_message)
        assert "→" not in rendered

    def test_custom_arrow_style(self) -> None:
        custom_arrow = ">"
        response = self._create_test_response(
            message=self._test_message,
            arrow_style=custom_arrow,
        )
        rendered = response.render()
        self._assert_contains_text(rendered, custom_arrow)
        assert "→" not in rendered
