"""Tests for TitlePromptResponse (titles)."""

from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_title_prompt_response_test import (
    AbstractTitlePromptResponseTest,
)


class TestTitlePromptResponse(AbstractTitlePromptResponseTest):
    """Focused tests for TitlePromptResponse rendering and options."""

    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.titles.title_prompt_response import (
            TitlePromptResponse,
        )

        return TitlePromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        kwargs = kwargs or {}
        kwargs.setdefault("text", self._test_message)
        # keep defaults: color=CYAN, character=DEFAULT, width=None
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # Title uses prefix "❯" and default fill character "⫻"
        self._assert_contains_text(rendered, "❯")
        self._assert_contains_text(rendered, "⫻")

    def get_expected_lines(self) -> int:
        # Titles render with an empty line before and after
        return 1

    # Keep default common structure from AbstractPromptResponseTest (expects blank lines)

    def test_renders_message_and_format(self) -> None:
        from wexample_prompt.responses.titles.title_prompt_response import (
            TitlePromptResponse,
        )

        response = TitlePromptResponse.create_title(text=self._test_message)
        response.render()
        self._assert_common_response_structure(response)
        self._assert_contains_text(response.rendered_content, self._test_message)
        self._assert_specific_format(response.rendered_content)

    def test_custom_character(self) -> None:
        from wexample_prompt.responses.titles.title_prompt_response import (
            TitlePromptResponse,
        )

        response = TitlePromptResponse.create_title(
            text=self._test_message, character="="
        )
        rendered = response.render()
        self._assert_contains_text(rendered, self._test_message)
        self._assert_contains_text(rendered, "=")
        assert (
            "⫻" not in rendered
        )  # default character should not appear when custom set
