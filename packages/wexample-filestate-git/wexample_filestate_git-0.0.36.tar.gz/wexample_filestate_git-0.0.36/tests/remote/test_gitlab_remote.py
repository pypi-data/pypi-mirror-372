from __future__ import annotations

from unittest.mock import patch

import pytest
from wexample_filestate_git.remote.gitlab_remote import GitlabRemote
from wexample_filestate_git.testing.git_remote_test import GitRemoteTest
from wexample_prompt.common.io_manager import IoManager


class TestGitlabRemote(GitRemoteTest):
    """Test cases for GitLab remote operations."""

    ENV_TOKEN_NAME = "GITLAB_API_TOKEN"
    SERVICE_CLASS = GitlabRemote

    @pytest.fixture
    def remote(self):
        io_manager = IoManager()
        with patch.dict("os.environ", {"GITLAB_API_TOKEN": "test_token"}):
            remote = GitlabRemote(io=io_manager)
            return remote

    def _assert_check_repository_exists_request(self, mock_request) -> None:
        """Assert the request parameters for checking repository existence."""
        assert (
            mock_request.call_args[1]["endpoint"]
            == f"projects/{self.test_namespace}%2F{self.test_repo_name}"
        )

    def _assert_create_repository_request(self, mock_request) -> None:
        """Assert the request parameters for creating a repository."""
        assert mock_request.call_args[1]["endpoint"] == "projects"
        assert mock_request.call_args[1]["data"]["name"] == self.test_repo_name

    def test_parse_repository_url_https(self, remote) -> None:
        url = "https://gitlab.com/test-namespace/test-repo.git"
        info = remote.parse_repository_url(url)
        assert info == {"name": "test-repo", "namespace": "test-namespace"}

    def test_parse_repository_url_ssh(self, remote) -> None:
        url = "git@gitlab.com:test-namespace/test-repo.git"
        info = remote.parse_repository_url(url)
        assert info == {"name": "test-repo", "namespace": "test-namespace"}

    def test_create_repository(self, remote) -> None:
        with patch(
            "wexample_helpers_api.common.abstract_gateway.AbstractGateway.make_request"
        ) as mock_request:
            mock_request.return_value.json.return_value = {"id": 1}

            result = remote.create_repository(
                name="test-repo",
                namespace="test-namespace",
                description="Test description",
                private=True,
            )

            mock_request.assert_called_once()
            self._assert_create_repository_request(mock_request)
            assert result == {"id": 1}

    def test_check_repository_exists(self, remote) -> None:
        with patch(
            "wexample_helpers_api.common.abstract_gateway.AbstractGateway.make_request"
        ) as mock_request:
            mock_request.return_value.status_code = 200

            exists = remote.check_repository_exists("test-repo", "test-namespace")

            mock_request.assert_called_once()
            self._assert_check_repository_exists_request(mock_request)
            assert exists is True
