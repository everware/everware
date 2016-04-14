from .. import GitMixin

def test_parser():
    tests = [
        (
            'https://github.com/aladagemre/django-notification.git@2927346f4c513a217ac8ad076e494dd1adbf70e1',
            'https://github.com/aladagemre/django-notification',
            '2927346f4c513a217ac8ad076e494dd1adbf70e1'
        ),
        (
            'https://github.com/USER/REPO/tree/BRANCH_OR_COMMIT/',
            'https://github.com/USER/REPO',
            'BRANCH_OR_COMMIT'
        ),
        (
            'https://github.com/USER/REPO.git@BRANCH_OR_COMMIT',
            'https://github.com/USER/REPO',
            'BRANCH_OR_COMMIT'
        ),
        (
            'https://github.com/astiunov/everware-dimuon-example/commit/e4912ae86178ba4e8f8de05513ccd6592d237233',
            'https://github.com/astiunov/everware-dimuon-example',
            'e4912ae86178ba4e8f8de05513ccd6592d237233',
        ),
        (
            'https://github.com/everware/everware-dimuon-example/',
            'https://github.com/everware/everware-dimuon-example',
            'HEAD'
        ),
        (
            'https://github.com/everware/everware.git',
            'https://github.com/everware/everware',
            'HEAD'
        )
    ]

    parser = GitMixin()

    for url, repo_url, repo_pointer in tests:
        parser.parse_url(url, '')
        assert parser.repo_url == repo_url, 'in url %s' % url
        assert parser._repo_pointer == repo_pointer, 'in url %s' % url
