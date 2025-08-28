from __future__ import annotations

from wexample_prompt.testing.abstract_prompt_test import AbstractPromptTest


class TestIoManager(AbstractPromptTest):
    def test_instantiate_class(self) -> None:
        from wexample_prompt.testing.resources.classes.class_with_io_methods import (
            ClassWithIoMethods,
        )

        instance = ClassWithIoMethods(io=self._io)
        assert instance.log(message="test instantiate class") is not None

    def test_instantiate_extended_base_model(self) -> None:
        from wexample_prompt.testing.resources.classes.extended_base_model_with_io_methods import (
            ExtendedBaseModelWithIoMethods,
        )

        instance = ExtendedBaseModelWithIoMethods(io=self._io)
        assert instance.log(message="test instantiate base model") is not None
