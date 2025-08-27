# THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.project_tpls v0.3.49
""" setup of aedev namespace-root: aedev namespace root, providing setup, development and documentation tools/templates for Python projects.. """
# noinspection PyUnresolvedReferences
import sys
print(f"SetUp {__name__=} {sys.executable=} {sys.argv=} {sys.path=}")

# noinspection PyUnresolvedReferences
import setuptools

setup_kwargs = {
    'author': 'AndiEcker',
    'author_email': 'aecker2@gmail.com',
    'classifiers': [       'Development Status :: 3 - Alpha', 'Natural Language :: English', 'Operating System :: OS Independent',
        'Programming Language :: Python', 'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9', 'Topic :: Software Development', 'Typing :: Typed'],
    'description': ('aedev namespace-root: aedev namespace root, providing setup, development and documentation tools/templates for '
 'Python projects.'),
    'extras_require': {       'dev': [       'aedev_setup_project', 'aedev_tpl_project', 'aedev_tpl_namespace_root', 'aedev_tpl_app',
                       'aedev_git_repo_manager', 'aedev_pythonanywhere', 'aedev_setup_hook', 'aedev_project_tpls',
                       'aedev_app_tpls', 'aedev_namespace_root_tpls', 'aedev_project_manager', 'sphinx',
                       'sphinx-rtd-theme', 'sphinx_autodoc_typehints', 'sphinx_paramlinks', 'ae_dev_ops', 'anybadge',
                       'coverage-badge', 'aedev_git_repo_manager', 'flake8', 'mypy', 'pylint', 'pytest', 'pytest-cov',
                       'pytest-django', 'typing', 'types-setuptools', 'wheel', 'twine'],
        'docs': ['sphinx', 'sphinx-rtd-theme', 'sphinx_autodoc_typehints', 'sphinx_paramlinks', 'ae_dev_ops'],
        'tests': [       'anybadge', 'coverage-badge', 'aedev_git_repo_manager', 'flake8', 'mypy', 'pylint', 'pytest',
                         'pytest-cov', 'pytest-django', 'typing', 'types-setuptools', 'wheel', 'twine']},
    'install_requires': [],
    'keywords': ['configuration', 'development', 'environment', 'productivity'],
    'license': 'GPL-3.0-or-later',
    'long_description': ('<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.namespace_root_tpls v0.3.18 -->\n'
 '# __aedev__ namespace-root project\n'
 '\n'
 'aedev namespace-root: aedev namespace root, providing setup, development and documentation tools/templates for '
 'Python projects.\n'
 '\n'
 '\n'
 '## aedev namespace root package use-cases\n'
 '\n'
 'this package is the root project of the aedev namespace and their portions (the modules\n'
 'and sub-packages of the namespace aedev). it provides helpers and templates in order to\n'
 'bundle and ease the maintenance, for example to:\n'
 '\n'
 '* update and deploy common outsourced files, optionally generated from templates.\n'
 '* merge docstrings of all portions into a single combined and cross-linked documentation.\n'
 '* compile and publish documentation via Sphinx onto [ReadTheDocs](https://aedev.readthedocs.io "aedev on RTD").\n'
 '* bulk refactor multiple portions of this namespace simultaneously using the\n'
 '  [git repository manager tool (__grm__)](https://gitlab.com/aedev-group/aedev_git_repo_manager).\n'
 '\n'
 'to enable the update and deployment of outsourced files generated from the templates provided by\n'
 'this root package, add this root package to the development requirements file (dev_requirements.txt)\n'
 'of each portion project of this namespace. in this entry you can optionally specify the version of\n'
 'this project.\n'
 '\n'
 'and because this namespace-root package is only needed for development tasks, it will never need to\n'
 'be added to the installation requirements file (requirements.txt) of a project.\n'
 '\n'
 'please check the [git repository manager manual](\n'
 'https://aedev.readthedocs.io/en/latest/man/git_repo_manager.html "git_repo_manager manual")\n'
 'for more detailed information on the provided actions of the __grm__ tool.\n'
 '\n'
 '\n'
 '## installation\n'
 '\n'
 'no installation is needed to use this project for your portion projects, because the __grm__ tool is\n'
 'automatically fetching this and the other template projects from https://gitlab.com/aedev-group (and\n'
 'in the specified version).\n'
 '\n'
 'an installation is only needed if you want to adapt this namespace-root project for your needs or if you want\n'
 'to contribute to this root package. in this case please follow the instructions given in the\n'
 ':ref:`contributing` document.\n'
 '\n'
 '\n'
 '## namespace portions\n'
 '\n'
 'the following 11 portions are currently included in this namespace:\n'
 '\n'
 '* [aedev_setup_project](https://pypi.org/project/aedev_setup_project "aedev namespace portion aedev_setup_project")\n'
 '* [aedev_tpl_project](https://pypi.org/project/aedev_tpl_project "aedev namespace portion aedev_tpl_project")\n'
 '* [aedev_tpl_namespace_root](https://pypi.org/project/aedev_tpl_namespace_root "aedev namespace portion '
 'aedev_tpl_namespace_root")\n'
 '* [aedev_tpl_app](https://pypi.org/project/aedev_tpl_app "aedev namespace portion aedev_tpl_app")\n'
 '* [aedev_git_repo_manager](https://pypi.org/project/aedev_git_repo_manager "aedev namespace portion '
 'aedev_git_repo_manager")\n'
 '* [aedev_pythonanywhere](https://pypi.org/project/aedev_pythonanywhere "aedev namespace portion '
 'aedev_pythonanywhere")\n'
 '* [aedev_setup_hook](https://pypi.org/project/aedev_setup_hook "aedev namespace portion aedev_setup_hook")\n'
 '* [aedev_project_tpls](https://pypi.org/project/aedev_project_tpls "aedev namespace portion aedev_project_tpls")\n'
 '* [aedev_app_tpls](https://pypi.org/project/aedev_app_tpls "aedev namespace portion aedev_app_tpls")\n'
 '* [aedev_namespace_root_tpls](https://pypi.org/project/aedev_namespace_root_tpls "aedev namespace portion '
 'aedev_namespace_root_tpls")\n'
 '* [aedev_project_manager](https://pypi.org/project/aedev_project_manager "aedev namespace portion '
 'aedev_project_manager")\n'),
    'long_description_content_type': 'text/markdown',
    'name': 'aedev_aedev',
    'package_data': {'': ['templates/de_spt_namespace-root_de_otf_de_tpl_README.md']},
    'packages': ['aedev.aedev', 'aedev.aedev.templates'],
    'project_urls': {       'Bug Tracker': 'https://gitlab.com/aedev-group/aedev_aedev/-/issues',
        'Documentation': 'https://aedev.readthedocs.io/en/latest/_autosummary/aedev.aedev.html',
        'Repository': 'https://gitlab.com/aedev-group/aedev_aedev',
        'Source': 'https://aedev.readthedocs.io/en/latest/_modules/aedev/aedev.html'},
    'python_requires': '>=3.9',
    'setup_requires': [],
    'url': 'https://gitlab.com/aedev-group/aedev_aedev',
    'version': '0.3.26',
    'zip_safe': False,
}

if __name__ == "__main__":
    setuptools.setup(**setup_kwargs)
    pass
