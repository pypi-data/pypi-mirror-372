"""Tests for ErrorPromptResponse."""

from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_prompt_message_response_test import (
    AbstractPromptMessageResponseTest,
)


class TestErrorPromptResponse(AbstractPromptMessageResponseTest):
    """Test cases for ErrorPromptResponse."""

    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.messages.error_prompt_response import (
            ErrorPromptResponse,
        )

        return ErrorPromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        kwargs = kwargs or {}
        kwargs.setdefault("message", self._test_message)
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # Error messages should include the error symbol
        self._assert_contains_text(rendered, "❌")

    def get_expected_lines(self) -> int:
        return 1  # Error messages are single line

    def test_simple_error_is_red(self) -> None:
        pass

        response = self._create_test_response()
        rendered = response.render()
        self._assert_contains_text(rendered, self._test_message)
        # Expect red color sequence
        self._assert_contains_text(rendered, "\u001b[31m")

    def test_error_with_exception_header_red_and_trace_present(self) -> None:
        # Create a sample exception
        try:
            raise ValueError("boom")
        except Exception as e:
            response = self._create_test_response(
                {"message": "Error with exception", "exception": e}
            )

        rendered = response.render()
        lines = rendered.split("\n")

        # At least two lines: header + trace
        assert len(lines) >= 2

        # First line should contain symbol, message and be red
        self._assert_contains_text(lines[0], "❌")
        self._assert_contains_text(lines[0], "Error with exception")
        self._assert_contains_text(lines[0], "\u001b[31m")

        # Trace lines should include the exception message or type
        trace_text = "\n".join(lines[1:])
        # At least the exception message should be present
        self._assert_contains_text(trace_text, "boom")
        # Often the type is included by the formatter; if not, message check above suffices
        # (No strict color assertions on the trace to avoid coupling to formatter internals)
