from __future__ import annotations

from wexample_prompt.common.io_manager import IoManager
from wexample_prompt.testing.abstract_prompt_test import AbstractPromptTest


class TestIoManager(AbstractPromptTest):
    def test_instantiate_class(self) -> None:
        from wexample_prompt.testing.resources.classes.class_with_io_manager import (
            ClassWithIoManager,
        )

        instance = ClassWithIoManager()
        assert instance.io is None

        self.assertClassHasNoneManager(ClassWithIoManager)
        self.assertClassInstanceSucceeded(ClassWithIoManager)

    def test_instantiate_class_required(self) -> None:
        from wexample_prompt.testing.resources.classes.class_with_required_io_manager import (
            ClassWithRequiredIoManager,
        )

        # Missing required 'io' should raise a TypeError from __init__
        self.assertMissingArgumentError(class_type=ClassWithRequiredIoManager)
        self.assertClassInstanceSucceeded(class_type=ClassWithRequiredIoManager)

    def test_instantiate_extended_base_model(self) -> None:
        from wexample_prompt.testing.resources.classes.extended_base_model_with_io_manager import (
            ExtendedBaseModelWithIoManager,
        )

        self.assertClassHasNoneManager(ExtendedBaseModelWithIoManager)
        self.assertClassInstanceSucceeded(ExtendedBaseModelWithIoManager)

    def test_instantiate_extended_base_model_required(self) -> None:
        from wexample_prompt.testing.resources.classes.extended_base_model_with_required_io_manager import (
            ExtendedBaseModelWithRequiredIoManager,
        )

        self.assertMissingArgumentError(ExtendedBaseModelWithRequiredIoManager)
        self.assertClassInstanceSucceeded(ExtendedBaseModelWithRequiredIoManager)

    def assertClassHasNoneManager(self, class_type: type) -> None:
        instance = class_type()
        assert instance.io is None

    def assertMissingArgumentError(self, class_type: type) -> None:
        with self.assertRaises(TypeError):
            class_type()

    def assertClassInstanceSucceeded(self, class_type: type) -> None:
        instance = class_type(io=self._io)
        assert isinstance(instance.io, IoManager)
