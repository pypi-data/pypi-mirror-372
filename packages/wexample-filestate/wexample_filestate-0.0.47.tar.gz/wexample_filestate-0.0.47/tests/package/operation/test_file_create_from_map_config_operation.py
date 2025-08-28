from __future__ import annotations

import os

from wexample_config.const.types import DictConfig
from wexample_filestate.config_option.children_filter_config_option import (
    ChildrenFilterConfigOption,
)
from wexample_filestate.const.disk import DiskItemType
from wexample_filestate.item.item_target_file import ItemTargetFile
from wexample_filestate.testing.test_abstract_operation import TestAbstractOperation


class TestFileCreateFromMapConfigOperation(TestAbstractOperation):
    missing_file_name: str = "simple-readme.md"

    def _operation_test_setup_configuration(self) -> DictConfig | None:
        pass

        from wexample_config.const.types import DictConfig

        class TestClass(ItemTargetFile):
            def prepare_value(self, config: DictConfig | None = None) -> DictConfig:
                config.update()

                return config

        return {
            "children": [
                {
                    "name": "collection",
                    "type": DiskItemType.DIRECTORY,
                    "children": [
                        {
                            "name": "one",
                            "type": DiskItemType.DIRECTORY,
                            "children": [
                                ChildrenFilterConfigOption(
                                    pattern={
                                        "class": TestClass,
                                        "name_pattern": r"^test-collection-[a-z]+-[a-z]+\.txt$",
                                        "type": DiskItemType.FILE,
                                        "should_exist": False,
                                    }
                                ),
                                ChildrenFilterConfigOption(
                                    pattern={
                                        "class": TestClass,
                                        "name_pattern": r"^test-directory-[a-z]$",
                                        "type": DiskItemType.DIRECTORY,
                                        "should_exist": True,
                                        "children": [
                                            {
                                                "name": "file.txt",
                                                "should_exist": True,
                                            }
                                        ],
                                    }
                                ),
                            ],
                        }
                    ],
                }
            ]
        }

    def _operation_get_count(self) -> int:
        return 3

    def _operation_test_assert_initial(self) -> None:
        target_file = self.state_manager.find_by_name_recursive(
            "test-collection-one-one.txt"
        )

        assert os.path.exists(target_file.get_resolved()), "The file should exist"

    def _operation_test_assert_applied(self) -> None:
        target_file = self.state_manager.find_by_name_recursive(
            "test-collection-one-one.txt"
        )

        assert not os.path.exists(
            target_file.get_resolved()
        ), "The target file have been removed because it matches the name pattern"
