"""Tests for TablePromptResponse."""

from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_prompt_response_test import (
    AbstractPromptResponseTest,
)


class TestTablePromptResponse(AbstractPromptResponseTest):
    """Test cases for TablePromptResponse."""

    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.data.table_prompt_response import (
            TablePromptResponse,
        )

        return TablePromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        kwargs = kwargs or {}
        kwargs.setdefault("headers", ["Name", "Age", "City"])
        kwargs.setdefault(
            "data",
            [
                ["John", "30", "New York"],
                ["Jane", "25", "San Francisco"],
                ["Bob", "35", "Chicago"],
            ],
        )
        kwargs.setdefault("title", self._test_message)
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # Should include table borders/separators
        self.assertTrue("|" in rendered or "+" in rendered)

    def get_expected_lines(self) -> int:
        # Empty lines (2) + title (1) + header (1) + 2 separators + 3 data rows
        return 9

    def test_create_table_without_headers(self) -> None:
        from wexample_prompt.responses.data.table_prompt_response import (
            TablePromptResponse,
        )

        response = TablePromptResponse.create_table(
            data=[
                ["John", "30", "New York"],
                ["Jane", "25", "San Francisco"],
            ]
        )
        rendered = response.render()
        self._assert_contains_text(rendered, "John")
        self._assert_contains_text(rendered, "30")
        self._assert_contains_text(rendered, "New York")

    def test_empty_table(self) -> None:
        from wexample_prompt.responses.data.table_prompt_response import (
            TablePromptResponse,
        )

        response = TablePromptResponse.create_table(data=[])
        rendered = response.render()
        assert rendered.strip() == ""

    def test_single_column(self) -> None:
        from wexample_prompt.responses.data.table_prompt_response import (
            TablePromptResponse,
        )

        data = [["Row 1"], ["Row 2"]]
        headers = ["Header"]
        response = TablePromptResponse.create_table(data=data, headers=headers)
        rendered = response.render()
        self._assert_contains_text(rendered, "Header")
        self._assert_contains_text(rendered, "Row 1")
        self._assert_contains_text(rendered, "Row 2")

    def test_column_alignment(self) -> None:
        from wexample_prompt.responses.data.table_prompt_response import (
            TablePromptResponse,
        )

        response = TablePromptResponse.create_table(
            data=[
                ["John", "30", "New York"],
                ["Jane", "25", "San Francisco"],
            ],
            headers=["Name", "Age", "City"],
        )
        rendered = response.render()
        lines = [l for l in rendered.split("\n") if l.strip()]
        for line in lines:
            if not line.startswith("+"):
                assert line.startswith("|")
                assert line.endswith("|")
