from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_prompt_message_response_test import (
    AbstractPromptMessageResponseTest,
)


class TestDebugPromptResponse(AbstractPromptMessageResponseTest):
    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.messages.debug_prompt_response import (
            DebugPromptResponse,
        )

        return DebugPromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        kwargs = kwargs or {}
        kwargs.setdefault("message", self._test_message)
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # Debug messages should include the debug symbol
        self._assert_contains_text(rendered, "🔍")

    def get_expected_lines(self) -> int:
        return 1  # Debug messages are single line

    def test_multiline_response(self) -> None:
        """Test multiline response."""
        self._asset_response_render_is_multiline(
            response=self._create_test_response(
                {"message": self._test_message_multiline}
            )
        )
