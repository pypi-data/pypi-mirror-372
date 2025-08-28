from __future__ import annotations

from wexample_config.const.types import DictConfig
from wexample_filestate.const.disk import DiskItemType
from wexample_filestate.testing.test_abstract_operation import TestAbstractOperation
from wexample_filestate_git.test.mixin.test_git_state_manager_mixin import (
    TestGitFileStateManagerMixin,
)


class TestGitRemoteAddOperation(TestGitFileStateManagerMixin, TestAbstractOperation):
    def _operation_test_setup_configuration(self) -> DictConfig | None:
        self._remove_test_git_dir()

        return {
            "children": [
                {
                    "name": "test_git_dir",
                    "should_exist": True,
                    "type": DiskItemType.DIRECTORY,
                    "git": {
                        "remote": [
                            {
                                "name": "github",
                                "url": lambda target: f"test-remote-with-{target.get_path().name}",
                            },
                        ]
                    },
                }
            ]
        }

    def _operation_get_count(self) -> int:
        return 2

    def _operation_test_assert_initial(self) -> None:
        self._assert_dir_exists(self._get_git_dir_path("test_git_dir"), positive=False)

    def _operation_test_assert_applied(self) -> None:
        self._assert_dir_exists(self._get_git_dir_path("test_git_dir"))
