"""Test multiple prompt response."""

from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.enums.verbosity_level import VerbosityLevel
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_prompt_response_test import (
    AbstractPromptResponseTest,
)


class TestMultiplePromptResponse(AbstractPromptResponseTest):
    """Test multiple prompt response."""

    def get_expected_lines(self) -> int:
        # Default case builds a single LogPromptResponse
        return 1

    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.data.multiple_prompt_response import (
            MultiplePromptResponse,
        )

        return MultiplePromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        from wexample_prompt.responses.log_prompt_response import LogPromptResponse

        kwargs = kwargs or {}
        message = kwargs.get("message", self._test_message)
        verbosity = kwargs.get("verbosity", VerbosityLevel.DEFAULT)
        responses = kwargs.get(
            "responses",
            [
                LogPromptResponse.create_log(
                    message=message,
                    verbosity=verbosity,
                )
            ],
        )
        kwargs["responses"] = responses
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # No specific formatting required for multiple wrapper
        pass

    def test_empty_responses(self) -> None:
        from wexample_prompt.responses.data.multiple_prompt_response import (
            MultiplePromptResponse,
        )

        rendered = MultiplePromptResponse.create_multiple(responses=[]).render()
        assert rendered is None

    def test_single_response(self) -> None:
        response = self._create_test_response()
        rendered = response.render()
        self._assert_contains_text(rendered, self._test_message)

    def test_multiple_responses_join(self) -> None:
        from wexample_prompt.responses.data.multiple_prompt_response import (
            MultiplePromptResponse,
        )
        from wexample_prompt.responses.log_prompt_response import LogPromptResponse

        responses = [
            LogPromptResponse.create_log(message="First"),
            LogPromptResponse.create_log(message="Second"),
            LogPromptResponse.create_log(message="Last"),
        ]
        from wexample_prompt.common.prompt_context import PromptContext

        rendered = MultiplePromptResponse.create_multiple(responses=responses).render(
            context=PromptContext(colorized=False)
        )
        assert rendered == "First\nSecond\nLast"

    def test_append_and_extend(self) -> None:
        from wexample_prompt.common.prompt_context import PromptContext
        from wexample_prompt.responses.data.multiple_prompt_response import (
            MultiplePromptResponse,
        )
        from wexample_prompt.responses.log_prompt_response import LogPromptResponse

        mr = MultiplePromptResponse.create_multiple(
            responses=[LogPromptResponse.create_log(message="Initial")]
        )
        mr.append_response(LogPromptResponse.create_log(message="Appended"))
        mr.extend_responses(
            [
                LogPromptResponse.create_log(message="Ext 1"),
                LogPromptResponse.create_log(message="Ext 2"),
            ]
        )
        rendered = mr.render(context=PromptContext(colorized=False))
        assert rendered == "Initial\nAppended\nExt 1\nExt 2"
