from __future__ import annotations

from wexample_filestate.testing.abstract_state_manager_test import (
    AbstractStateManagerTest,
)
from wexample_filestate_git.test.mixin.test_git_state_manager_mixin import (
    TestGitFileStateManagerMixin,
)


class TestGitFileStateManager(TestGitFileStateManagerMixin, AbstractStateManagerTest):
    def test_setup(self) -> None:
        from wexample_filestate_git.operations_provider.git_operations_provider import (
            GitOperationsProvider,
        )
        from wexample_filestate_git.options_provider.git_options_provider import (
            GitOptionsProvider,
        )

        assert GitOptionsProvider in self.state_manager.options_providers
        assert GitOperationsProvider in self.state_manager.operations_providers
