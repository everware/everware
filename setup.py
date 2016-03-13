#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import os
import sys
import shutil
from subprocess import check_call
from glob import glob

v = sys.version_info
if v[:2] < (3,3):
    error = "ERROR: Jupyter Hub requires Python version 3.3 or above."
    print(error, file=sys.stderr)
    sys.exit(1)

def mtime(path):
    """shorthand for mtime"""
    return os.stat(path).st_mtime


if os.name in ('nt', 'dos'):
    error = "ERROR: Windows is not supported"
    print(error, file=sys.stderr)

# At least we're on the python version we need, move on.

from distutils.core import setup

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))

from distutils.cmd import Command
from distutils.command.build_py import build_py
from distutils.command.sdist import sdist

npm_path = ':'.join([
    pjoin(here, 'node_modules', '.bin'),
    os.environ.get("PATH", os.defpath),
])

here = os.path.abspath(os.path.dirname(__file__))
share = pjoin(here, 'share')
static = pjoin(share, 'static')

class BaseCommand(Command):
    """Dumb empty command because Command needs subclasses to override too much"""
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def get_inputs(self):
        return []
    
    def get_outputs(self):
        return []

class Bower(BaseCommand):
    description = "fetch static client-side components with bower"
    
    user_options = []
    bower_dir = pjoin(static, 'components')
    node_modules = pjoin(here, 'node_modules')
    
    def should_run(self):
        if not os.path.exists(self.bower_dir):
            return True
        return mtime(self.bower_dir) < mtime(pjoin(here, 'bower.json'))

    def should_run_npm(self):
        if not shutil.which('npm'):
            print("npm unavailable", file=sys.stderr)
            return False
        if not os.path.exists(self.node_modules):
            return True
        return mtime(self.node_modules) < mtime(pjoin(here, 'package.json'))
    
    def run(self):
        if not self.should_run():
            print("bower dependencies up to date")
            return
        
        if self.should_run_npm():
            print("installing build dependencies with npm")
            check_call(['npm', 'install'], cwd=here)
            os.utime(self.node_modules)
        
        env = os.environ.copy()
        env['PATH'] = npm_path
        
        try:
            check_call(
                ['bower', 'install', '--allow-root', '--config.interactive=false'],
                cwd=here,
                env=env,
            )
        except OSError as e:
            print("Failed to run bower: %s" % e, file=sys.stderr)
            print("You can install js dependencies with `npm install`", file=sys.stderr)
            raise
        os.utime(self.bower_dir)
        # update data-files in case this created new files
        self.distribution.data_files = get_data_files()


class CSS(BaseCommand):
    description = "compile CSS from LESS"
    
    def should_run(self):
        """Does less need to run?"""
        # from IPython.html.tasks.py
        
        css_targets = [pjoin(static, 'css', 'style.min.css')]
        css_maps = [t + '.map' for t in css_targets]
        targets = css_targets + css_maps
        if not all(os.path.exists(t) for t in targets):
            # some generated files don't exist
            return True
        earliest_target = sorted(mtime(t) for t in targets)[0]
    
        # check if any .less files are newer than the generated targets
        for (dirpath, dirnames, filenames) in os.walk(static):
            for f in filenames:
                if f.endswith('.less'):
                    path = pjoin(static, dirpath, f)
                    timestamp = mtime(path)
                    if timestamp > earliest_target:
                        return True
    
        return False
    
    def run(self):
        if not self.should_run():
            print("CSS up-to-date")
            return
        
        self.run_command('js')
        
        style_less = pjoin(static, 'less', 'style.less')
        style_css = pjoin(static, 'css', 'style.min.css')
        sourcemap = style_css + '.map'
        
        env = os.environ.copy()
        env['PATH'] = npm_path
        try:
            check_call([
                'lessc', '--clean-css',
                '--source-map-basepath={}'.format(static),
                '--source-map={}'.format(sourcemap),
                '--source-map-rootpath=../',
                style_less, style_css,
            ], cwd=here, env=env)
        except OSError as e:
            print("Failed to run lessc: %s" % e, file=sys.stderr)
            print("You can install js dependencies with `npm install`", file=sys.stderr)
            raise
        # update data-files in case this created new files
        self.distribution.data_files = get_data_files()

def get_data_files():
    """Get data files in share/jupyter"""
    
    data_files = []
    ntrim = len(here) + 1
    
    for (d, dirs, filenames) in os.walk(static):
        data_files.append((
            d[ntrim:],
            [ pjoin(d, f) for f in filenames ]
        ))
    return data_files


setup_args = dict(
    name                = 'everware',
    packages            = ['everware'],
    scripts             = glob(pjoin('scripts', '*')),
    version             = '0.0.0',
    description         = """Everware""",
    long_description    = "",
    author              = "",
    author_email        = "",
    url                 = "",
    license             = "BSD",
    platforms           = "Linux, Mac OS X",
    keywords            = ['Interactive', 'Interpreter', 'Shell', 'Web'],
    classifiers         = [
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)

setup_args['cmdclass'] = {'js': Bower, 'css': CSS}

# setuptools requirements
if 'setuptools' in sys.modules:
    setup_args['install_requires'] = install_requires = []
    with open('requirements.txt') as f:
        for line in f.readlines():
            req = line.strip()
            if not req or req.startswith(('-e', '#')):
                continue
            install_requires.append(req)


def main():
    setup(**setup_args)

if __name__ == '__main__':
    main()
