# THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.project_tpls v0.3.49
""" setup of aedev namespace package portion namespace_root_tpls: templates and outsourced files for namespace root projects.. """
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
        'Programming Language :: Python :: 3.9', 'Topic :: Software Development :: Libraries :: Python Modules',
        'Typing :: Typed'],
    'description': 'aedev namespace package portion namespace_root_tpls: templates and outsourced files for namespace root projects.',
    'extras_require': {       'dev': [       'aedev_project_tpls', 'aedev_aedev', 'anybadge', 'coverage-badge', 'aedev_git_repo_manager',
                       'flake8', 'mypy', 'pylint', 'pytest', 'pytest-cov', 'pytest-django', 'typing',
                       'types-setuptools', 'wheel', 'twine'],
        'docs': [],
        'tests': [       'anybadge', 'coverage-badge', 'aedev_git_repo_manager', 'flake8', 'mypy', 'pylint', 'pytest',
                         'pytest-cov', 'pytest-django', 'typing', 'types-setuptools', 'wheel', 'twine']},
    'install_requires': [],
    'keywords': ['configuration', 'development', 'environment', 'productivity'],
    'license': 'GPL-3.0-or-later',
    'long_description': ('<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.aedev v0.3.25 -->\n'
 '<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.tpl_namespace_root V0.3.14 -->\n'
 '# namespace_root_tpls 0.3.18\n'
 '\n'
 '[![GitLab '
 'develop](https://img.shields.io/gitlab/pipeline/aedev-group/aedev_namespace_root_tpls/develop?logo=python)](\n'
 '    https://gitlab.com/aedev-group/aedev_namespace_root_tpls)\n'
 '[![LatestPyPIrelease](\n'
 '    https://img.shields.io/gitlab/pipeline/aedev-group/aedev_namespace_root_tpls/release0.3.17?logo=python)](\n'
 '    https://gitlab.com/aedev-group/aedev_namespace_root_tpls/-/tree/release0.3.17)\n'
 '[![PyPIVersions](https://img.shields.io/pypi/v/aedev_namespace_root_tpls)](\n'
 '    https://pypi.org/project/aedev-namespace-root-tpls/#history)\n'
 '\n'
 '>aedev namespace package portion namespace_root_tpls: templates and outsourced files for namespace root projects..\n'
 '\n'
 '[![Coverage](https://aedev-group.gitlab.io/aedev_namespace_root_tpls/coverage.svg)](\n'
 '    https://aedev-group.gitlab.io/aedev_namespace_root_tpls/coverage/index.html)\n'
 '[![MyPyPrecision](https://aedev-group.gitlab.io/aedev_namespace_root_tpls/mypy.svg)](\n'
 '    https://aedev-group.gitlab.io/aedev_namespace_root_tpls/lineprecision.txt)\n'
 '[![PyLintScore](https://aedev-group.gitlab.io/aedev_namespace_root_tpls/pylint.svg)](\n'
 '    https://aedev-group.gitlab.io/aedev_namespace_root_tpls/pylint.log)\n'
 '\n'
 '[![PyPIImplementation](https://img.shields.io/pypi/implementation/aedev_namespace_root_tpls)](\n'
 '    https://gitlab.com/aedev-group/aedev_namespace_root_tpls/)\n'
 '[![PyPIPyVersions](https://img.shields.io/pypi/pyversions/aedev_namespace_root_tpls)](\n'
 '    https://gitlab.com/aedev-group/aedev_namespace_root_tpls/)\n'
 '[![PyPIWheel](https://img.shields.io/pypi/wheel/aedev_namespace_root_tpls)](\n'
 '    https://gitlab.com/aedev-group/aedev_namespace_root_tpls/)\n'
 '[![PyPIFormat](https://img.shields.io/pypi/format/aedev_namespace_root_tpls)](\n'
 '    https://pypi.org/project/aedev-namespace-root-tpls/)\n'
 '[![PyPILicense](https://img.shields.io/pypi/l/aedev_namespace_root_tpls)](\n'
 '    https://gitlab.com/aedev-group/aedev_namespace_root_tpls/-/blob/develop/LICENSE.md)\n'
 '[![PyPIStatus](https://img.shields.io/pypi/status/aedev_namespace_root_tpls)](\n'
 '    https://libraries.io/pypi/aedev-namespace-root-tpls)\n'
 '[![PyPIDownloads](https://img.shields.io/pypi/dm/aedev_namespace_root_tpls)](\n'
 '    https://pypi.org/project/aedev-namespace-root-tpls/#files)\n'
 '\n'
 '\n'
 '## installation\n'
 '\n'
 '\n'
 'execute the following command to install the\n'
 'aedev.namespace_root_tpls package\n'
 'in the currently active virtual environment:\n'
 ' \n'
 '```shell script\n'
 'pip install aedev-namespace-root-tpls\n'
 '```\n'
 '\n'
 'if you want to contribute to this portion then first fork\n'
 '[the aedev_namespace_root_tpls repository at GitLab](\n'
 'https://gitlab.com/aedev-group/aedev_namespace_root_tpls "aedev.namespace_root_tpls code repository").\n'
 'after that pull it to your machine and finally execute the\n'
 'following command in the root folder of this repository\n'
 '(aedev_namespace_root_tpls):\n'
 '\n'
 '```shell script\n'
 'pip install -e .[dev]\n'
 '```\n'
 '\n'
 'the last command will install this package portion, along with the tools you need\n'
 'to develop and run tests or to extend the portion documentation. to contribute only to the unit tests or to the\n'
 'documentation of this portion, replace the setup extras key `dev` in the above command with `tests` or `docs`\n'
 'respectively.\n'
 '\n'
 'more detailed explanations on how to contribute to this project\n'
 '[are available here](\n'
 'https://gitlab.com/aedev-group/aedev_namespace_root_tpls/-/blob/develop/CONTRIBUTING.rst)\n'
 '\n'
 '\n'
 '## namespace portion documentation\n'
 '\n'
 'information on the features and usage of this portion are available at\n'
 '[ReadTheDocs](\n'
 'https://aedev.readthedocs.io/en/latest/_autosummary/aedev.namespace_root_tpls.html\n'
 '"aedev_namespace_root_tpls documentation").\n'),
    'long_description_content_type': 'text/markdown',
    'name': 'aedev_namespace_root_tpls',
    'package_data': {       '': [       'templates/de_otf_de_tpl_README.md',
                    'templates/de_mtp_templates/de_otf_de_spt_namespace-root_de_otf_de_tpl_README.md',
                    'templates/de_sfp_docs/de_otf_de_tpl_index.rst',
                    'templates/de_sfp_docs/features_and_examples.rst']},
    'packages': [       'aedev.namespace_root_tpls', 'aedev.namespace_root_tpls.templates',
        'aedev.namespace_root_tpls.templates.de_mtp_templates', 'aedev.namespace_root_tpls.templates.de_sfp_docs'],
    'project_urls': {       'Bug Tracker': 'https://gitlab.com/aedev-group/aedev_namespace_root_tpls/-/issues',
        'Documentation': 'https://aedev.readthedocs.io/en/latest/_autosummary/aedev.namespace_root_tpls.html',
        'Repository': 'https://gitlab.com/aedev-group/aedev_namespace_root_tpls',
        'Source': 'https://aedev.readthedocs.io/en/latest/_modules/aedev/namespace_root_tpls.html'},
    'python_requires': '>=3.9',
    'setup_requires': [],
    'url': 'https://gitlab.com/aedev-group/aedev_namespace_root_tpls',
    'version': '0.3.18',
    'zip_safe': False,
}

if __name__ == "__main__":
    setuptools.setup(**setup_kwargs)
    pass
