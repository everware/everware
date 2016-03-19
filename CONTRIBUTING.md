# Contributing

`everware` is an open source project, and we welcome contributions of all kinds

To report a bug, open an issue on our [issue tracker][issues].

Contributors to the project are required to follow the [code of
conduct](CONDUCT.md).

By contributing, you are agreeing that we may redistribute your work under
[these licenses][license].

We use the [fork and pull][gh-fork-pull] model to manage changes. More information
about [forking a repository][gh-fork] and [making a Pull Request][gh-pull].

To contribute to this repository:

1. create an issue to explain what problem you are tackling and discuss
   how you plan to tackle it. Or comment on an existing issue saying you
   want to tackle it.
1. fork [the project repository](https://github.com/everware/everware/).
   Click on the 'Fork' button near the top of the page. This creates a copy of
   the code under your account on the GitHub server.
2. clone this copy of the repository to your local disk:

        $ git clone git@github.com:YourLogin/everware.git
        $ cd everware

2. create a new branch in your clone `git checkout -b my-new-branch`. Never
   work in the ``master`` branch!
4. Work on this copy on your computer using Git to do the version
   control. When you're done editing, run:

          $ git add modified_files
          $ git commit

   to record your changes in Git, then push them to GitHub with:

          $ git push -u origin my-new-branch

Finally, go to the web page of your fork of the `everware` repository,
and click 'Pull request' to send your changes to the maintainers for
review. This will send an email to the committers. A valid PR includes
the following items:

* a description of the problem you are solving
* a discussion why you made the choices you made
* contains the minimal set of changes needed to solve the problem (do
  not mix several issues, rather create separate PRs)
* unit and frontend tests for your changes
* the code should follow the style of the project
* the code should contain documentation in the form of docstrings
  and comments
* no commits merging master into your branch, instead rebase your branch

We encourage you to start your PR as soon as possible to get feedback early.
Mark it as `[WIP] your subject` if it is not ready for merging. We will try and
respond as quickly as possible, but we are all volunteers so it might take 24h.
Maintainers, please leave some time for others to think and respond before
merging.

We prefer "getting it right" and having a maintainable project over chasing
features or doing things in a hurry.

Expect to get feedback and suggestions for improvement. This is not a sign that
you are stupid, instead it shows the others care about your changes and want to
make them better and help you out with things you missed.

There is one additional rule: no one can merge their own pull requests, someone
else has to press the button.

[issues]: https://github.com/everware/everware/issues
[license]: LICENSE
[gh-fork]: https://help.github.com/articles/fork-a-repo/
[gh-pull]: https://help.github.com/articles/using-pull-requests/
[gh-fork-pull]: https://help.github.com/articles/using-pull-requests/#fork--pull
