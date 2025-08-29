"""Tests for ChoicePromptResponse (interactive)."""

from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_prompt_response_test import (
    AbstractPromptResponseTest,
)


class TestChoicePromptResponse(AbstractPromptResponseTest):
    """Test cases for ChoicePromptResponse."""

    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.interactive.choice_prompt_response import (
            ChoicePromptResponse,
        )

        return ChoicePromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        kwargs = kwargs or {}
        kwargs.setdefault("question", self._test_message)
        kwargs.setdefault("choices", ["Option 1", "Option 2"])
        kwargs.setdefault("predefined_answer", "Option 2")
        # keep default abort ("> Abort") behavior unless overridden
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # Choice prompts should have arrow indicators and numbering
        self._assert_contains_text(rendered, "›")
        self._assert_contains_text(rendered, "⨯")

    def get_expected_lines(self) -> int:
        # By default: question (1) + 2 choices + abort (1)
        return 5

    # Override: interactive choice does not render leading empty line.
    def _assert_common_response_structure(
        self, response: AbstractPromptResponse
    ) -> None:
        lines = response.rendered_content.split("\n")
        assert len(lines) == self.get_expected_lines()
        # First line should be the question text
        self._assert_contains_text(lines[0], self._test_message)
        # Each choice line should be properly formatted
        for i, choice in enumerate(["Option 1", "Option 2"], start=1):
            choice_line = lines[i]
            self._assert_contains_text(choice_line, choice)

    def test_create_with_choice_objects(self) -> None:
        from wexample_prompt.responses.interactive.choice_prompt_response import (
            ChoicePromptResponse,
        )

        choices = {
            "value1": "Display 1",
            "value2": "Display 2",
        }

        response = ChoicePromptResponse.create_choice(
            question=self._test_message,
            choices=choices,
            predefined_answer="value2",
        )

        response.render()

        self._assert_contains_text(response.rendered_content, "Display 1")
        self._assert_contains_text(response.rendered_content, "Display 2")
        assert "value1" not in response.rendered_content
        assert "value2" not in response.rendered_content

    def test_abort_option(self) -> None:
        abort_text = "Cancel"
        response = self._create_test_response(abort=abort_text)
        response.render()
        self._assert_contains_text(response.rendered_content, abort_text)
        # abort should be numbered after the choices
        self._assert_contains_text(
            response.rendered_content, str(len(["Option 1", "Option 2"]) + 1)
        )

    def test_no_abort_option(self) -> None:
        response = self._create_test_response(abort=None)
        response.render()

        assert "> Abort" not in response.rendered_content
        # question + 2 choices
        non_empty = [l for l in response.rendered_content.split("\n") if l.strip()]
        assert len(non_empty) == self.get_expected_lines()

    def test_multiline_question_does_not_crash_and_renders_both_lines(self) -> None:
        from wexample_prompt.responses.interactive.choice_prompt_response import (
            ChoicePromptResponse,
        )

        question = "What to do?\nPick wisely"
        response = ChoicePromptResponse.create_choice(
            question=question,
            choices=["One", "Two"],
            predefined_answer="Two",
        )

        # Should not raise
        response.render()

        content = response.rendered_content
        assert "What to do?" in content
        assert "Pick wisely" in content
