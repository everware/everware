import git
import re
from tornado import gen
from concurrent.futures import ThreadPoolExecutor


class GitExecutor:
    def __init__(self, repo_url, tmp_dir):
        """parse repo_url to parts:
        _processed: url to clone from
        _repo_pointer: position to reset"""

        if repo_url.startswith('git://'):
            raise ValueError("git protocol isn't supported yet")
        self._repo_url = repo_url
        self._repo_dir = tmp_dir
        self._repo_pointer = None
        if '@' in repo_url:
            self._processed_repo_url, self._repo_pointer = repo_url.split('@')
        else:
            parts = re.match(
                r'(^.+?://[^/]+/[^/]+/.+?)(?:/|$)(tree|commit)?(/[^/]+)?',
                repo_url
            )
            if not parts:
                raise ValueError('Incorrect repository url')
            self._processed_repo_url = parts.group(1)
            if parts.group(3):
                self._repo_pointer = parts.group(3)[1:]
        if (self._processed_repo_url.startswith('https') and
            self._processed_repo_url.endswith('.git')):
            self._processed_repo_url = self._processed_repo_url[:-4]
        if not self._repo_pointer:
            self._repo_pointer = 'HEAD'

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
    def exec(self):
        yield self.git('clone', self._processed_repo_url, self._repo_dir)
        repo = git.Repo(self._repo_dir)
        repo.git.reset('--hard', self._repo_pointer)
        self._repo_sha = repo.rev_parse('HEAD')
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
    def processed_repo_url(self):
        return self._processed_repo_url

    @property
    def repo_sha(self):
        return self._repo_sha

    @property
    def branch_name(self):
        return self._branch_name
