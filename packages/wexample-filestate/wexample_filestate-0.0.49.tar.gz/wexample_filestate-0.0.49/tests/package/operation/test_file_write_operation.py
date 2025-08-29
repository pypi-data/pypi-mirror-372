from __future__ import annotations

from wexample_config.const.types import DictConfig
from wexample_filestate.testing.test_abstract_operation import TestAbstractOperation
from wexample_helpers.helpers.file import file_read, file_write


class TestFileWriteOperation(TestAbstractOperation):
    test_file_name: str = "test-should-contain-lines.txt"
    initial_content: str = "Initial line 1\nInitial line 2"
    required_lines: list = ["Required line 1", "Required line 2"]

    def _operation_test_setup_configuration(self) -> DictConfig | None:
        from wexample_filestate.const.disk import DiskItemType

        return {
            "children": [
                {
                    "name": self.test_file_name,
                    "type": DiskItemType.FILE,
                    "should_contain_lines": self.required_lines,
                },
            ]
        }

    def _operation_get_count(self) -> int:
        return 1

    def _operation_test_setup(self) -> None:
        super()._operation_test_setup()

        # Create file with initial content
        target_file = self.state_manager.find_by_name_or_fail(self.test_file_name)
        file_write(target_file.get_resolved(), self.initial_content)

    def _operation_test_assert_initial(self) -> None:
        target_file = self.state_manager.find_by_name_or_fail(self.test_file_name)
        content = file_read(target_file.get_resolved())

        # Check initial content is correct
        assert content == self.initial_content, "Initial content should be unchanged"

        # Check required lines are not present yet
        for line in self.required_lines:
            assert (
                line not in content.splitlines()
            ), f"Required line '{line}' should not be present yet"

    def _operation_test_assert_applied(self) -> None:
        target_file = self.state_manager.find_by_name_or_fail(self.test_file_name)
        content = file_read(target_file.get_resolved())
        lines = content.splitlines()

        # Check initial content is preserved
        assert "Initial line 1" in lines, "Original content should be preserved"
        assert "Initial line 2" in lines, "Original content should be preserved"

        # Check required lines were added
        for required_line in self.required_lines:
            assert (
                required_line in lines
            ), f"Required line '{required_line}' should have been added"
