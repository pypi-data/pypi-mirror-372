"""Tests for ConfirmPromptResponse (interactive)."""

from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_prompt_response_test import (
    AbstractPromptResponseTest,
)


class TestConfirmPromptResponse(AbstractPromptResponseTest):
    """Test cases for ConfirmPromptResponse."""

    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.interactive.confirm_prompt_response import (
            ConfirmPromptResponse,
        )

        return ConfirmPromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        kwargs = kwargs or {}
        kwargs.setdefault("question", self._test_message)
        kwargs.setdefault("choices", None)  # default YES/NO
        kwargs.setdefault("predefined_answer", "yes")
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # Box borders and options format
        self._assert_contains_text(rendered, "-")
        self._assert_contains_text(rendered, "[")
        self._assert_contains_text(rendered, "]")

    def get_expected_lines(self) -> int:
        # Box layout: top border + empty + question + empty + options + empty + bottom border
        return 7

    # Override: confirm renders a boxed layout with specific structure
    def _assert_common_response_structure(
        self, response: AbstractPromptResponse
    ) -> None:
        lines = response.rendered_content.split("\n")
        assert len(lines) == self.get_expected_lines()
        # Question should appear
        self._assert_contains_text(response.rendered_content, self._test_message)
        # Options (default YES/NO) should appear
        self._assert_contains_text(response.rendered_content, "[y: Yes]")
        self._assert_contains_text(response.rendered_content, "[n: No]")

    def test_multiline_question_does_not_crash_and_renders_all_lines(self) -> None:
        from wexample_prompt.responses.interactive.confirm_prompt_response import (
            ConfirmPromptResponse,
        )

        question = "Proceed?\nThis will modify files"
        response = ConfirmPromptResponse.create_confirm(
            question=question,
            predefined_answer="yes",
        )

        # Should not raise
        response.render()

        content = response.rendered_content
        assert "Proceed?" in content
        assert "This will modify files" in content
