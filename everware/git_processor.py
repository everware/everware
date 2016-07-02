import re
import git
from concurrent.futures import ThreadPoolExecutor
from tornado import gen


class GitMixin:
    STATE_VARS = ['_repo_url', '_repo_dir', '_repo_pointer', '_processed_repo_url',
            '_protocol', '_service', '_owner', '_repo', '_token', '_repo_sha', '_branch_name']

    def parse_url(self, repo_url, tmp_dir=None):
        """parse repo_url to parts:
        _processed: url to clone from
        _repo_pointer: position to reset"""

        self._repo_url = repo_url
        self._repo_dir = tmp_dir
        self._repo_pointer = None
        if re.search(r'@\w+/?$', repo_url):
            self._processed_repo_url, self._repo_pointer = repo_url.rsplit('@', 1)
            if self._repo_pointer.endswith('/'):
                self._repo_pointer = self._repo_pointer[:-1]
        else:
            parts = re.match(
                r'(^.+?://[^/]+/[^/]+/.+?)(?:/|$)(tree|commits?)?(/[^/]+)?', # github and bitbucket
                repo_url
            )
            if not parts:
                raise ValueError('Incorrect repository url')
            self._processed_repo_url = parts.group(1)
            if parts.group(3):
                self._repo_pointer = parts.group(3)[1:]
        if self._processed_repo_url.endswith('.git'):
            self._processed_repo_url = self._processed_repo_url[:-4]
        if not self._repo_pointer:
            self._repo_pointer = 'HEAD'

        url_parts = re.match(r'^(.+?)://([^/]+)/([^/]+)/(.+)/?$', self._processed_repo_url)
        if not url_parts:
            raise ValueError('Incorrect repository url')
        self._protocol, self._service, self._owner, self._repo = url_parts.groups()
        self._token = None

        for not_supported_protocol in ('ssh',):
            if not_supported_protocol in self._protocol.lower():
                raise ValueError("%s isn't supported yet" % not_supported_protocol)

        if '@' in self._service:
            token, self._service = self._service.split('@')
            if re.match(r'\w+:x-oauth-basic', token):
                token, _ = token.split(':')
            self._token = token
            self._processed_repo_url = '{proto}://{service}/{owner}/{repo}'.format(
                proto=self._protocol,
                service=self._service,
                owner=self._owner,
                repo=self._repo
            )

    _git_executor = None
    @property
    def git_executor(self):
        """single global git executor"""
        cls = self.__class__
        if cls._git_executor is None:
            cls._git_executor = ThreadPoolExecutor(20)
        return cls._git_executor

    _git_client = None
    @property
    def git_client(self):
        """single global git client instance"""
        cls = self.__class__
        if cls._git_client is None:
            cls._git_client = git.Git()
        return cls._git_client

    def _git(self, method, *args, **kwargs):
        """wrapper for calling git methods

        to be passed to ThreadPoolExecutor
        """
        m = getattr(self.git_client, method)
        return m(*args, **kwargs)

    def git(self, method, *args, **kwargs):
        """Call a git method in a background thread

        returns a Future
        """
        return self.git_executor.submit(self._git, method, *args, **kwargs)

    @gen.coroutine
    def prepare_local_repo(self):
        clone_url = self.repo_url_with_token
        yield self.git('clone', clone_url, self._repo_dir)
        repo = git.Repo(self._repo_dir)
        repo.git.reset('--hard', self._repo_pointer)
        self._repo_sha = repo.rev_parse('HEAD').hexsha
        self._branch_name = repo.active_branch.name

    @property
    def escaped_repo_url(self):
        repo_url = re.sub(r'^.+?://', '', self._processed_repo_url)
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        trans = str.maketrans(':/-.', "____")
        repo_url = repo_url.translate(trans).lower()
        return re.sub(r'_+', '_', repo_url)

    @property
    def repo_url(self):
        return self._processed_repo_url

    @property
    def commit_sha(self):
        return self._repo_sha

    @property
    def branch_name(self):
        return self._branch_name

    @property
    def repo(self):
        return self._repo

    @property
    def owner(self):
        return self._owner

    @property
    def service(self):
        return self._service

    @property
    def token(self):
        return self._token

    @property
    def repo_url_with_token(self):
        cur_service = self._service
        if self.token:
            cur_service = self.token + '@' + cur_service
        return '{proto}://{service}/{owner}/{repo}'.format(
            proto=self._protocol,
            service=cur_service,
            owner=self._owner,
            repo=self._repo
        )

    def get_state(self):
        result = {key: getattr(self, key, '') for key in self.STATE_VARS}
        return result

    def load_state(self, state):
        for key in self.STATE_VARS:
            if key in state:
                setattr(self, key, state[key])

