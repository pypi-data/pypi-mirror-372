from __future__ import annotations

from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment


class TestPromptResponseLine:
    def test_create_basic_line(self) -> None:
        """Test creating a basic line with single segment."""
        segment = PromptResponseSegment(text="Hello")
        line = PromptResponseLine(segments=[segment])
        assert len(line.segments) == 1
        assert line.segments[0].text == "Hello"

    def test_line_to_string(self) -> None:
        from wexample_prompt.common.prompt_context import PromptContext

        """Test converting line to string."""
        segments = [
            PromptResponseSegment(text="Hello"),
            PromptResponseSegment(text=" World"),
        ]
        line = PromptResponseLine(segments=segments)
        assert line.render(context=PromptContext()) == "Hello World"

    def test_create_from_string_splits_multiline(self) -> None:
        """Multi-line input should be split into distinct PromptResponseLine without embedded newlines."""
        from wexample_prompt.common.prompt_context import PromptContext

        text = "Line A\nLine B\nLine C"
        lines = PromptResponseLine.create_from_string(text)

        assert len(lines) == 3
        rendered = [ln.render(context=PromptContext()) for ln in lines]
        assert rendered == ["Line A", "Line B", "Line C"]
        # No segment should contain newlines
        for ln in lines:
            for seg in ln.segments:
                assert "\n" not in seg.text

    def test_wrapping_is_per_line_not_across_lines(self) -> None:
        """Wrapping width must reset for each logical line produced by create_from_string."""
        from wexample_prompt.common.prompt_context import PromptContext

        text = "AAAAAA\nBBBBBB"
        lines = PromptResponseLine.create_from_string(text)
        assert len(lines) == 2

        r1 = lines[0].render(context=PromptContext(width=3, formatting=True))
        r2 = lines[1].render(context=PromptContext(width=3, formatting=True))

        # Expect chunking independently per line
        assert r1 == "AAA\nAAA"
        assert r2 == "BBB\nBBB"
