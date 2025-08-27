<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.namespace_root_tpls v0.3.18 -->
# __aedev__ namespace-root project

aedev namespace-root: aedev namespace root, providing setup, development and documentation tools/templates for Python projects.


## aedev namespace root package use-cases

this package is the root project of the aedev namespace and their portions (the modules
and sub-packages of the namespace aedev). it provides helpers and templates in order to
bundle and ease the maintenance, for example to:

* update and deploy common outsourced files, optionally generated from templates.
* merge docstrings of all portions into a single combined and cross-linked documentation.
* compile and publish documentation via Sphinx onto [ReadTheDocs](https://aedev.readthedocs.io "aedev on RTD").
* bulk refactor multiple portions of this namespace simultaneously using the
  [git repository manager tool (__grm__)](https://gitlab.com/aedev-group/aedev_git_repo_manager).

to enable the update and deployment of outsourced files generated from the templates provided by
this root package, add this root package to the development requirements file (dev_requirements.txt)
of each portion project of this namespace. in this entry you can optionally specify the version of
this project.

and because this namespace-root package is only needed for development tasks, it will never need to
be added to the installation requirements file (requirements.txt) of a project.

please check the [git repository manager manual](
https://aedev.readthedocs.io/en/latest/man/git_repo_manager.html "git_repo_manager manual")
for more detailed information on the provided actions of the __grm__ tool.


## installation

no installation is needed to use this project for your portion projects, because the __grm__ tool is
automatically fetching this and the other template projects from https://gitlab.com/aedev-group (and
in the specified version).

an installation is only needed if you want to adapt this namespace-root project for your needs or if you want
to contribute to this root package. in this case please follow the instructions given in the
:ref:`contributing` document.


## namespace portions

the following 11 portions are currently included in this namespace:

* [aedev_setup_project](https://pypi.org/project/aedev_setup_project "aedev namespace portion aedev_setup_project")
* [aedev_tpl_project](https://pypi.org/project/aedev_tpl_project "aedev namespace portion aedev_tpl_project")
* [aedev_tpl_namespace_root](https://pypi.org/project/aedev_tpl_namespace_root "aedev namespace portion aedev_tpl_namespace_root")
* [aedev_tpl_app](https://pypi.org/project/aedev_tpl_app "aedev namespace portion aedev_tpl_app")
* [aedev_git_repo_manager](https://pypi.org/project/aedev_git_repo_manager "aedev namespace portion aedev_git_repo_manager")
* [aedev_pythonanywhere](https://pypi.org/project/aedev_pythonanywhere "aedev namespace portion aedev_pythonanywhere")
* [aedev_setup_hook](https://pypi.org/project/aedev_setup_hook "aedev namespace portion aedev_setup_hook")
* [aedev_project_tpls](https://pypi.org/project/aedev_project_tpls "aedev namespace portion aedev_project_tpls")
* [aedev_app_tpls](https://pypi.org/project/aedev_app_tpls "aedev namespace portion aedev_app_tpls")
* [aedev_namespace_root_tpls](https://pypi.org/project/aedev_namespace_root_tpls "aedev namespace portion aedev_namespace_root_tpls")
* [aedev_project_manager](https://pypi.org/project/aedev_project_manager "aedev namespace portion aedev_project_manager")
