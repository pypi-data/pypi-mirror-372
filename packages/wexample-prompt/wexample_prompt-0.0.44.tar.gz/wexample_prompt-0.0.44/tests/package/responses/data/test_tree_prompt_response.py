"""Tests for TreePromptResponse."""

from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_prompt_response_test import (
    AbstractPromptResponseTest,
)


class TestTreePromptResponse(AbstractPromptResponseTest):
    """Test cases for TreePromptResponse."""

    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.data.tree_prompt_response import (
            TreePromptResponse,
        )

        return TreePromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        kwargs = kwargs or {}
        data = kwargs.setdefault(
            "data",
            {
                "root": {
                    "folder1": {"file1": "content1", "file2": "content2"},
                    "folder2": {"file3": "content3"},
                }
            },
        )
        # Ensure test message is present in the tree to satisfy base assertion
        data["root"][kwargs.pop("message", self._test_message)] = ""
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # Should include tree drawing characters
        self.assertIn("├", rendered)
        self.assertIn("└", rendered)
        self.assertIn("│", rendered)
        self.assertIn("──", rendered)

    def get_expected_lines(self) -> int:
        # Empty lines (1) + root (1) + folder1 (5 files) + folder2 (3 file) + test text (1) + empty (2)
        return 13

    def test_empty_tree(self) -> None:
        from wexample_prompt.responses.data.tree_prompt_response import (
            TreePromptResponse,
        )

        response = TreePromptResponse.create_tree(data={})
        rendered = response.render()
        assert rendered.strip() == ""

    def test_single_node(self) -> None:
        from wexample_prompt.responses.data.tree_prompt_response import (
            TreePromptResponse,
        )

        data = {"root": "value"}
        response = TreePromptResponse.create_tree(data=data)
        rendered = response.render()
        self._assert_contains_text(rendered, "root")
        self._assert_contains_text(rendered, "value")

    def test_deep_nesting(self) -> None:
        from wexample_prompt.responses.data.tree_prompt_response import (
            TreePromptResponse,
        )

        data = {"level1": {"level2": {"level3": {"level4": "value"}}}}
        response = TreePromptResponse.create_tree(data=data)
        rendered = response.render()
        for key in ("level1", "level2", "level3", "level4"):
            self._assert_contains_text(rendered, key)
        self._assert_contains_text(rendered, "value")
        # Indentation should increase with depth
        lines = [l for l in rendered.split("\n") if l.strip()]
        indents = [len(line) - len(line.lstrip()) for line in lines]
        assert sorted(indents) == indents

    def test_none_values(self) -> None:
        from wexample_prompt.responses.data.tree_prompt_response import (
            TreePromptResponse,
        )

        data = {"root": {"valid": "value", "none": None}}
        response = TreePromptResponse.create_tree(data=data)
        rendered = response.render()
        self._assert_contains_text(rendered, "root")
        self._assert_contains_text(rendered, "valid")
        self._assert_contains_text(rendered, "value")
        self._assert_contains_text(rendered, "none")
        assert "None" not in rendered
