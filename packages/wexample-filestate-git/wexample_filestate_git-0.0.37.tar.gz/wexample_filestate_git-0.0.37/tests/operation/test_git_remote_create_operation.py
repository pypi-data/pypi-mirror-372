from __future__ import annotations

from unittest.mock import patch

from wexample_config.const.types import DictConfig
from wexample_filestate.const.disk import DiskItemType
from wexample_filestate.testing.test_abstract_operation import TestAbstractOperation
from wexample_filestate_git.remote.github_remote import GithubRemote
from wexample_filestate_git.remote.gitlab_remote import GitlabRemote
from wexample_filestate_git.test.mixin.test_git_state_manager_mixin import (
    TestGitFileStateManagerMixin,
)


class TestGitRemoteCreateOperation(TestGitFileStateManagerMixin, TestAbstractOperation):
    def _operation_test_setup(self) -> None:
        # Setup all mocks
        self.mock_github_connect = patch.object(GithubRemote, "connect").start()
        self.mock_github_create_if_not_exists = patch.object(
            GithubRemote, "create_repository_if_not_exists"
        ).start()
        self.mock_gitlab_connect = patch.object(GitlabRemote, "connect").start()
        self.mock_gitlab_create_if_not_exists = patch.object(
            GitlabRemote, "create_repository_if_not_exists"
        ).start()

        # Configure default mock behaviors
        self.mock_github_create_if_not_exists.return_value = False
        self.mock_gitlab_create_if_not_exists.return_value = False

        # Call parent setup after mocks are ready
        super()._operation_test_setup()

    def _operation_test_setup_configuration(self) -> DictConfig | None:
        self._remove_test_git_dir()
        self._mock_git_env()

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
                                "type": "github",
                                "url": "https://github.com/test-namespace/test-repo.git",
                                "create_remote": True,
                            },
                            {
                                "name": "gitlab",
                                "type": "gitlab",
                                "url": "https://gitlab.com/test-namespace/test-repo.git",
                                "create_remote": True,
                            },
                        ]
                    },
                }
            ]
        }

    def _operation_get_count(self) -> int:
        return 3  # One operation for each remote, 1 operation to create local repo

    def _operation_test_assert_initial(self) -> None:
        # Verify initial state - no repositories should exist
        self.mock_github_create_if_not_exists.assert_not_called()
        self.mock_gitlab_create_if_not_exists.assert_not_called()

    def _operation_test_assert_applied(self) -> None:
        # Verify that repositories were created using the new interface
        self.mock_github_create_if_not_exists.assert_called_once_with(
            "https://github.com/test-namespace/test-repo.git"
        )

        self.mock_gitlab_create_if_not_exists.assert_called_once_with(
            "https://gitlab.com/test-namespace/test-repo.git"
        )

    def _operation_test_assert_rollback(self) -> None:
        # Add rollback assertions if needed
        pass
