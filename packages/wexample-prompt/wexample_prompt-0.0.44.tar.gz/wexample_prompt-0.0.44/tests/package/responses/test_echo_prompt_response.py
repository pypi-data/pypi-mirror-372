from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_prompt_response_test import (
    AbstractPromptResponseTest,
)


class TestEchoPromptResponse(AbstractPromptResponseTest):
    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.echo_prompt_response import EchoPromptResponse

        return EchoPromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        kwargs = kwargs or {}
        kwargs.setdefault("message", self._test_message)
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # Echo messages have no specific format to check
        pass

    def get_expected_lines(self) -> int:
        return 1  # Echo messages are single line by default

    def test_empty_response(self) -> None:
        """Test empty response."""
        from wexample_prompt.responses.echo_prompt_response import EchoPromptResponse

        response = EchoPromptResponse.create_echo(message="")
        self.assertEqual(response.render(), "")

    def test_multiline_response(self) -> None:
        """Test multiline response."""
        self._asset_response_render_is_multiline(
            response=self._get_response_class().create_echo(message=self._test_message_multiline)  # type: ignore[attr-defined]
        )

    def test_echo_width(self) -> None:
        assert self._io.terminal_width is not None

        # Echo a string using the terminal with length
        response = self._get_response_class().create_echo(
            **self._create_test_kwargs(
                kwargs={"message": self._io.terminal_width * "!"}
            )
        )
        response.render()

        # It should print only one line.
        self._assert_rendered_lines_count(response=response, lines_count=1)
