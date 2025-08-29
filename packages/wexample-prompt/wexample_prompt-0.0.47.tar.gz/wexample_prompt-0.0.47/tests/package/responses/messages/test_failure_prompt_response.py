"""Tests for FailurePromptResponse."""

from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_prompt_message_response_test import (
    AbstractPromptMessageResponseTest,
)


class TestFailurePromptResponse(AbstractPromptMessageResponseTest):
    """Test cases for FailurePromptResponse."""

    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.messages.failure_prompt_response import (
            FailurePromptResponse,
        )

        return FailurePromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        kwargs = kwargs or {}
        kwargs.setdefault("message", self._test_message)
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # Failure messages should include the failure symbol
        self._assert_contains_text(rendered, "❌")

    def get_expected_lines(self) -> int:
        return 1  # Failure messages are single line
