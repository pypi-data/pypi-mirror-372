"""Tests for SubtitlePromptResponse (titles)."""

from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_title_prompt_response_test import (
    AbstractTitlePromptResponseTest,
)


class TestSubtitlePromptResponse(AbstractTitlePromptResponseTest):
    """Focused tests for SubtitlePromptResponse rendering and options."""

    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.titles.subtitle_prompt_response import (
            SubtitlePromptResponse,
        )

        return SubtitlePromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        kwargs = kwargs or {}
        kwargs.setdefault("text", self._test_message)
        # keep defaults: color=BLUE, character=DEFAULT, width=None
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # Subtitle uses prefix with two spaces then ❯ and default fill char
        self._assert_contains_text(rendered, "  ❯")
        self._assert_contains_text(rendered, "⫻")

    def get_expected_lines(self) -> int:
        # Subtitles render with an empty line before and after
        return 1

    # Keep default common structure from AbstractPromptResponseTest (expects blank lines)

    def test_renders_message_and_format(self) -> None:
        from wexample_prompt.responses.titles.subtitle_prompt_response import (
            SubtitlePromptResponse,
        )

        response = SubtitlePromptResponse.create_subtitle(text=self._test_message)
        response.render()
        self._assert_common_response_structure(response)
        self._assert_contains_text(response.rendered_content, self._test_message)
        self._assert_specific_format(response.rendered_content)

    def test_custom_character(self) -> None:
        from wexample_prompt.responses.titles.subtitle_prompt_response import (
            SubtitlePromptResponse,
        )

        response = SubtitlePromptResponse.create_subtitle(
            text=self._test_message, character="."
        )
        rendered = response.render()
        self._assert_contains_text(rendered, self._test_message)
        self._assert_contains_text(rendered, ".")
        assert "-" not in rendered  # ensure default from legacy not used
