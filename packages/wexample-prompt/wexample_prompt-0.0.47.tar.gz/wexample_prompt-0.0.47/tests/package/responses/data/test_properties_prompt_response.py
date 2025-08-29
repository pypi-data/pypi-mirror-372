"""Tests for PropertiesPromptResponse."""

from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_prompt_response_test import (
    AbstractPromptResponseTest,
)


class TestPropertiesPromptResponse(AbstractPromptResponseTest):
    """Test cases for PropertiesPromptResponse."""

    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.data.properties_prompt_response import (
            PropertiesPromptResponse,
        )

        return PropertiesPromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        kwargs = kwargs or {}
        kwargs.setdefault("properties", {"name": "John Doe", "age": 30})
        kwargs.setdefault("title", self._test_message)
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # Should contain key-value formatting
        self.assertIn(":", rendered)

    def get_expected_lines(self) -> int:
        # Boxed properties typically render with top/bottom borders and content
        return 5

    def test_empty_properties(self) -> None:
        from wexample_prompt.responses.data.properties_prompt_response import (
            PropertiesPromptResponse,
        )

        response = PropertiesPromptResponse.create_properties(properties={})
        rendered = response.render()
        assert rendered == ""

    def test_simple_properties_rendering(self) -> None:
        response = self._create_test_response(
            properties={"name": "John Doe", "age": 30}
        )
        rendered = response.render()
        self._assert_contains_text(rendered, "name")
        self._assert_contains_text(rendered, "John Doe")
        self._assert_contains_text(rendered, "age")
        self._assert_contains_text(rendered, "30")
        self._assert_specific_format(rendered)

    def test_nested_properties_rendering(self) -> None:
        nested = {
            "personal": {"name": "John Doe", "age": 30},
            "contact": {"email": "john@example.com", "phone": "123-456-7890"},
        }
        from wexample_prompt.responses.data.properties_prompt_response import (
            PropertiesPromptResponse,
        )

        response = PropertiesPromptResponse.create_properties(
            properties=nested, title=self._test_message
        )
        rendered = response.render()
        # Section headers and nested values appear
        self._assert_contains_text(rendered, "personal")
        self._assert_contains_text(rendered, "contact")
        self._assert_contains_text(rendered, "John Doe")
        self._assert_contains_text(rendered, "123-456-7890")
        self._assert_specific_format(rendered)

    def test_with_custom_title(self) -> None:
        custom_title = "User Information"
        response = self._create_test_response(title=custom_title)
        rendered = response.render()
        self._assert_contains_text(rendered, custom_title)
        self._assert_specific_format(rendered)

    def test_custom_nested_indent(self) -> None:
        nested = {"level0": {"level1": {"key": "value"}}}
        from wexample_prompt.responses.data.properties_prompt_response import (
            PropertiesPromptResponse,
        )

        response = PropertiesPromptResponse.create_properties(
            properties=nested, nested_indent=4
        )
        rendered = response.render()
        # Expect at least one line with 4-space indentation
        assert any(line.startswith("    ") for line in rendered.splitlines())
        self._assert_specific_format(rendered)
