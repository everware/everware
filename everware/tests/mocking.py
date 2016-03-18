from jupyterhub.tests.conftest import MockHub
from everware.authenticator import GitHubOAuthenticator


class MockGitHubOAuthenticator(GitHubOAuthenticator):
    def _admin_users_default(self):
        return {'admin'}

    def authenticate(self, handler):
        print(handler)
        return ('octocat', '1234')


class MockWareHub(MockHub):
    def _authenticator_class_default(self):
        return MockGitHubOAuthenticator
