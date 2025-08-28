"""Tests for ProgressPromptResponse (interactive)."""

from __future__ import annotations

from wexample_helpers.const.types import Kwargs
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.testing.abstract_prompt_response_test import (
    AbstractPromptResponseTest,
)


class TestProgressPromptResponse(AbstractPromptResponseTest):
    """Focused tests for ProgressPromptResponse core rendering and validation."""

    def test_manager_indentation(self) -> None:
        # No indentation for interactive prints.
        pass

    def _get_response_class(self) -> type[AbstractPromptResponse]:
        from wexample_prompt.responses.interactive.progress_prompt_response import (
            ProgressPromptResponse,
        )

        return ProgressPromptResponse

    def _create_test_kwargs(self, kwargs=None) -> Kwargs:
        kwargs = kwargs or {}
        # Sensible defaults
        kwargs.setdefault("total", 10)
        kwargs.setdefault("current", 5)
        kwargs.setdefault("width", 20)
        kwargs.setdefault("label", self._test_message)
        return kwargs

    def _assert_specific_format(self, rendered: str) -> None:
        # Should contain percentage and progress characters
        self._assert_contains_text(rendered, "%")
        from wexample_prompt.responses.interactive.progress_prompt_response import (
            ProgressPromptResponse,
        )

        self._assert_contains_text(rendered, ProgressPromptResponse.FILL_CHAR)
        self._assert_contains_text(rendered, ProgressPromptResponse.EMPTY_CHAR)

    def get_expected_lines(self) -> int:
        # Progress bar is single line
        return 1

    # Override: progress does not have leading empty line.
    def _assert_common_response_structure(
        self, response: AbstractPromptResponse
    ) -> None:
        lines = response.rendered_content.split("\n")
        assert len(lines) == 1
        # Label should be present at start
        self._assert_contains_text(lines[0], self._test_message)
        # Should end with percentage
        assert lines[0].strip().endswith("%")

    def test_create_progress_renders_expected_percentage(self) -> None:
        from wexample_prompt.responses.interactive.progress_prompt_response import (
            ProgressPromptResponse,
        )

        response = ProgressPromptResponse.create_progress(
            total=10, current=5, width=20, label=self._test_message
        )
        rendered = response.render()
        self._assert_contains_text(rendered, "50%")

    def test_invalid_values_raise(self) -> None:
        import pytest
        from wexample_prompt.responses.interactive.progress_prompt_response import (
            ProgressPromptResponse,
        )

        with pytest.raises(ValueError):
            ProgressPromptResponse.create_progress(total=0, current=0)
        with pytest.raises(ValueError):
            ProgressPromptResponse.create_progress(total=10, current=1, width=0)

    def test_custom_style(self) -> None:
        from wexample_prompt.responses.interactive.progress_prompt_response import (
            ProgressPromptResponse,
        )

        old_fill = ProgressPromptResponse.FILL_CHAR
        old_empty = ProgressPromptResponse.EMPTY_CHAR
        try:
            ProgressPromptResponse.set_style(fill_char="#", empty_char="-")
            rendered = self._create_test_response().render()
            self._assert_contains_text(rendered, "#")
            self._assert_contains_text(rendered, "-")
        finally:
            ProgressPromptResponse.set_style(fill_char=old_fill, empty_char=old_empty)

    def test_caps_at_100_percent_and_full_bar(self) -> None:
        from wexample_prompt.responses.interactive.progress_prompt_response import (
            ProgressPromptResponse,
        )

        resp = self._create_test_response(total=10, current=20, width=10, label=None)
        rendered = resp.render()
        self._assert_contains_text(rendered, "100%")
        # When full, there should be no EMPTY_CHAR present inside the bar segment
        assert ProgressPromptResponse.EMPTY_CHAR not in rendered.split("%")[0]

    def test_progress_width(self) -> None:
        # Echo a string using the terminal with length
        response = self._io.progress(total=20, current=10)
        self._assert_rendered_lines_count(response=response, lines_count=1)

        response = self._io.progress(label="With a label", total=20, current=10)
        self._assert_rendered_lines_count(response=response, lines_count=1)

    def test_handle_updates_with_manager(self) -> None:
        """Using IoManager: render once, then update via handle and check output string."""
        from wexample_prompt.enums.terminal_color import TerminalColor

        response = self._io.progress(
            label="Progress via IoManager",
            total=100,
            current=0,
        )
        handle = response.get_handle()
        # Update to 25%
        out = handle.update(
            current=25, label="Io progress 25%", color=TerminalColor.YELLOW
        )
        assert isinstance(out, str)
        self._assert_contains_text(out, "25%")
        self._assert_contains_text(out, "Io progress 25%")

    def test_handle_updates_standalone_and_finish(self) -> None:
        """Standalone usage: create, render, then update via handle and finish."""
        from wexample_prompt.enums.terminal_color import TerminalColor
        from wexample_prompt.responses.interactive.progress_prompt_response import (
            ProgressPromptResponse,
        )

        # Create standalone response
        resp = ProgressPromptResponse.create_progress(
            label="Standalone",
            total=80,
            current=0,
            color=TerminalColor.CYAN,
        )
        first = resp.render()
        assert isinstance(first, str)
        handle = resp.get_handle()
        # Move to 50%
        out = handle.update(current=40, label="Standalone 40/80")
        self._assert_contains_text(out, "50%")
        self._assert_contains_text(out, "Standalone 40/80")
        # Finish
        out2 = handle.finish()
        self._assert_contains_text(out2, "100%")

    def test_child_range_mapping_and_percentage(self) -> None:
        """Child handle maps its local current to the parent's absolute current."""
        response = self._io.progress(label="Global", total=1000)
        root = response.get_handle()
        # Start at an absolute position
        root.update(current=50, label="init")
        # Create child that spans from current to a target end
        child = root.create_range_handle(to=350)
        # Move inside child by 50 units -> parent should be start(50) + 50 = 100
        out = child.update(current=50, label="child move")
        assert response.current == 100
        # Advance child by 50% of its range (range total=300 => +150) -> parent 250
        out2 = child.advance(step="50%", label="child +50%")
        assert response.current == 250
        # Rendered strings exist
        assert isinstance(out, str)
        assert isinstance(out2, str)

    def test_nested_children_finish(self) -> None:
        """Nested children can finish and update the shared response current at each level."""
        response = self._io.progress(label="Global", total=1000)
        root = response.get_handle()
        root.update(current=100, label="root init")
        lvl1 = root.create_range_handle(to=600)  # child of root
        lvl1.update(current="20%", label="lvl1 update")  # -> parent ~200
        lvl2 = lvl1.create_range_handle(to=500)  # child of lvl1
        lvl2.advance(step="50%", label="lvl2 advance")  # halfway inside lvl2
        # Level 3 then finishes -> parent current should equal lvl3 end
        lvl3 = lvl2.create_range_handle(to=450)
        out = lvl3.finish(label="lvl3 finish")
        assert response.current == 450
        assert isinstance(out, str)
