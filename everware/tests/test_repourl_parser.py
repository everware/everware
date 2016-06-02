from .. import GitMixin

def test_parser():
    tests = [
        (
            'https://github.com/aladagemre/django-notification.git@2927346f4c513a217ac8ad076e494dd1adbf70e1',
            'https://github.com/aladagemre/django-notification',
            '2927346f4c513a217ac8ad076e494dd1adbf70e1',
            'https',
            'github.com',
            'aladagemre',
            'django-notification'
        ),
        (
            'https://github.com/USER/REPO/tree/BRANCH_OR_COMMIT/',
            'https://github.com/USER/REPO',
            'BRANCH_OR_COMMIT',
            'https',
            'github.com',
            'USER',
            'REPO',
        ),
        (
            'https://github.com/USER/REPO.git@BRANCH_OR_COMMIT',
            'https://github.com/USER/REPO',
            'BRANCH_OR_COMMIT',
            'https',
            'github.com',
            'USER',
            'REPO',
        ),
        (
            'https://github.com/astiunov/everware-dimuon-example/commit/e4912ae86178ba4e8f8de05513ccd6592d237233',
            'https://github.com/astiunov/everware-dimuon-example',
            'e4912ae86178ba4e8f8de05513ccd6592d237233',
            'https',
            'github.com',
            'astiunov',
            'everware-dimuon-example',
        ),
        (
            'https://github.com/everware/everware-dimuon-example/',
            'https://github.com/everware/everware-dimuon-example',
            'HEAD',
            'https',
            'github.com',
            'everware',
            'everware-dimuon-example'
        ),
        (
            'https://github.com/everware/everware.git',
            'https://github.com/everware/everware',
            'HEAD',
            'https',
            'github.com',
            'everware',
            'everware'
        ),
        (
            'https://bitbucket.org/_perlik/everware-dimuon-example/commits/9bec6770485eb6b245648bc251d045a204973cc9',
            'https://bitbucket.org/_perlik/everware-dimuon-example',
            '9bec6770485eb6b245648bc251d045a204973cc9',
            'https',
            'bitbucket.org',
            '_perlik',
            'everware-dimuon-example'
        ),
        (
            'https://abacaba@github.com/owner/repo.git',
            'https://github.com/owner/repo',
            'HEAD',
            'https',
            'github.com',
            'owner',
            'repo',
            'abacaba'
        ),
        (
            'https://abacaba:x-oauth-basic@github.com/owner/repo.git@somehash',
            'https://github.com/owner/repo',
            'somehash',
            'https',
            'github.com',
            'owner',
            'repo',
            'abacaba'
        )
    ]

    parser = GitMixin()

    for cur_test in tests:
        token = None
        if len(cur_test) == 8:
            url, repo_url, repo_pointer, proto, service, owner, repo, token = cur_test
        else:
            url, repo_url, repo_pointer, proto, service, owner, repo = cur_test

        parser.parse_url(url, '')
        error_message = 'in url %s' % url
        assert parser.repo_url == repo_url, error_message
        assert parser._repo_pointer == repo_pointer, error_message
        assert parser._protocol == proto, error_message
        assert parser.service == service, error_message
        assert parser.owner == owner, error_message
        assert parser.repo == repo, error_message
        assert parser.token == token, error_message
