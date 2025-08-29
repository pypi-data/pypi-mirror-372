"""Tests for BufferOutputHandler."""

from __future__ import annotations

from wexample_prompt.output.buffer_output_handler import BufferOutputHandler
from wexample_prompt.testing.abstract_prompt_test import AbstractPromptTest


class TestBufferOutputHandler(AbstractPromptTest):
    def test_print_buffers_response_and_returns_rendered(self) -> None:
        # Switch IoManager to buffer output handler
        self._io.output = BufferOutputHandler()

        # Call a simple echo to produce a response
        response = self._io.echo("Buffered output")

        # Should return a string (rendered output)
        assert isinstance(response.rendered_content, str)
        assert "Buffered output" in response.rendered_content

        # Buffer should contain exactly one response object
        assert isinstance(self._io.output, BufferOutputHandler)
        assert len(self._io.output.responses) == 1

        # The buffered item should be a response with matching render
        buffered_response = self._io.output.responses[0]
        assert buffered_response.render() == response.rendered_content
