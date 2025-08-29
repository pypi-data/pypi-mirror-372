from __future__ import annotations

from wexample_prompt.testing.abstract_prompt_test import AbstractPromptTest


class TestIoManager(AbstractPromptTest):
    def test_class_indentation_levels(self) -> None:
        from wexample_prompt.testing.resources.classes.class_indenation_level_one import (
            ClassIndentationLevelOne,
        )

        level_one = ClassIndentationLevelOne(io=self._io)
        level_one.print_deep_log_one()

        assert level_one is not None
