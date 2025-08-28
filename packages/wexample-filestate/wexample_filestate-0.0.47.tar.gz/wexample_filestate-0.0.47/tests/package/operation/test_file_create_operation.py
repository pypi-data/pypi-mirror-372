from __future__ import annotations

import os

from wexample_config.const.types import DictConfig
from wexample_filestate.testing.test_abstract_operation import TestAbstractOperation


class TestFileCreateOperation(TestAbstractOperation):
    missing_file_name: str = "simple-text-missing.txt"
    missing_dir_name: str = "simple-directory-missing"

    def _operation_test_setup_configuration(self) -> DictConfig | None:
        from wexample_filestate.const.disk import DiskItemType

        return {
            "children": [
                {
                    "name": self.missing_dir_name,
                    "should_exist": True,
                    "type": DiskItemType.DIRECTORY,
                },
                {
                    "name": self.missing_file_name,
                    "should_exist": True,
                    "type": DiskItemType.FILE,
                    "default_content": "This is a test",
                },
            ]
        }

    def _operation_get_count(self) -> int:
        # Will create a file and a directory.
        return 2

    def _operation_test_assert_initial(self) -> None:
        target_dir = self.state_manager.find_by_name_or_fail(self.missing_dir_name)
        target_file = self.state_manager.find_by_name_or_fail(self.missing_file_name)

        assert not os.path.exists(
            target_dir.get_resolved()
        ), "The directory should not exist"
        assert not os.path.exists(
            target_file.get_resolved()
        ), "The file should not exist"

    def _operation_test_assert_applied(self) -> None:
        target_dir = self.state_manager.find_by_name_or_fail(self.missing_dir_name)
        target_file = self.state_manager.find_by_name_or_fail(self.missing_file_name)

        assert os.path.exists(
            target_dir.get_resolved()
        ), "The target directory should have been created"
        assert os.path.exists(
            target_file.get_resolved()
        ), "The target file should have been created"
