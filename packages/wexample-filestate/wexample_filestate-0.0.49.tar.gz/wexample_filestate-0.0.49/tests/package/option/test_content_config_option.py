from __future__ import annotations

from wexample_config.const.types import DictConfig
from wexample_filestate.const.test import TEST_FILE_NAME_SIMPLE_TEXT
from wexample_filestate.testing.test_abstract_operation import TestAbstractOperation


class TestContentConfigOption(TestAbstractOperation):
    missing_file_name: str = "simple-text-missing.txt"
    missing_dir_name: str = "simple-directory-missing"
    test_content: str = "CHANGED_CONTENT"

    def _operation_test_setup_configuration(self) -> DictConfig | None:
        from wexample_filestate.const.disk import DiskItemType

        return {
            "children": [
                {
                    "name": TEST_FILE_NAME_SIMPLE_TEXT,
                    "should_exist": True,
                    "type": DiskItemType.FILE,
                    "content": self.test_content,
                }
            ]
        }

    def _operation_get_count(self) -> int:
        # Will create a file and a directory.
        return 1

    def _operation_test_assert_initial(self) -> None:
        self._assert_file_content_equals(
            file_path=self._get_absolute_path_from_state_manager(
                TEST_FILE_NAME_SIMPLE_TEXT
            ),
            expected_value=self.test_content,
            positive=False,
        )

    def _operation_test_assert_applied(self) -> None:
        self._assert_file_content_equals(
            file_path=self._get_absolute_path_from_state_manager(
                TEST_FILE_NAME_SIMPLE_TEXT
            ),
            expected_value=self.test_content,
            positive=True,
        )
