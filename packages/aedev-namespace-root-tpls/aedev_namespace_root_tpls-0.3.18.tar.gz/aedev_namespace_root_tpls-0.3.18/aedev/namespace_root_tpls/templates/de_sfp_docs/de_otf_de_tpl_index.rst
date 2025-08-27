namespace portions documentation
################################

welcome to the documentation of the portions (app/service modules and sub-packages) of this freely extendable
{namespace_name} namespace (:pep:`420`).


.. include:: features_and_examples.rst


code maintenance guidelines
***************************


portions code requirements
==========================

    * pure python
    * fully typed (:pep:`526`)
    * fully :ref:`documented <{namespace_name}-portions>`
    * 100 % test coverage
    * multi thread save
    * code checks (using pylint and flake8)


design pattern and software principles
======================================

    * `DRY - don't repeat yourself <http://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`__
    * `KIS - keep it simple <http://en.wikipedia.org/wiki/Keep_it_simple_stupid>`__


.. include:: ../CONTRIBUTING.rst


create new namespace
====================

a :pep:`420` namespace splits the codebase of a library or framework into multiple project repositories, called
portions (of the namespace).

.. hint::
    the `aedev` namespace is providing `the grm tool to create and maintain any namespace and its portions
    <https://aedev.readthedocs.io/en/latest/man/git_repo_manager.html>`__.

the id of a new namespace consists of letters only and has to be available on PYPI. the group-name name gets by default
generated from the namespace name plus the suffix ``'-group'``, so best choose an id that results in a group name that
is available on your repository server.


register a new namespace portion
================================

follow the steps underneath to add and register a new module as portion onto the `{namespace_name}` namespace:

1. open a console window and change the current directory to the parent directory of your projects root folders.
2. choose a not-existing/unique name for the new portion (referred as `<portion-name>` in the next steps).
3. run ``grm --namespace={namespace_name} --project=<portion_name> new-module`` to register the portion
   name within the namespace, to create a new project folder `{namespace_name}_<portion-name>` (providing
   initial project files created from templates) and to get a pre-configured git repository (with the remote
   already set and the initial files unstaged, to be extended, staged and finally committed).
4. run ``cd {namespace_name}_<portion-name>`` to change the current to the working tree root
   of the new portion project.
5. run `pyenv local venv_name <https://pypi.org/project/pyenv/>`__ (or any other similar tool) to
   create/prepare a local virtual environment.
6. fans of TDD are then coding unit tests in the prepared test module `test_{namespace_name}_<portion-name>{PY_EXT}`,
   situated within the `{TESTS_FOLDER}` sub-folder of your new code project folder.
7. extend the file <portion_name>{PY_EXT} situated in the `{namespace_name}` sub-folder to implement the new portion.
8. run ``grm check-integrity`` to run the linting and unit tests (if they fail go one or two steps back).
9. run ``grm prepare``, then amend the commit message within the file `{COMMIT_MSG_FILE_NAME}`,
   then run ``grm commit`` and ``grm push`` to commit and upload your new portion to your personal
   forked repository onto the origin remote server, and finally run ``grm request`` to request the merge/pull into
   the fork/upstream repository of the user/group `{repo_group}` (at {repo_root}).

the registration of a new portion to the {namespace_name} namespace has to be done by a namespace maintainer.

registered portions will automatically be included into the `{namespace_name} namespace documentation`, available at
`ReadTheDocs <{docs_root}>`__.



.. _{namespace_name}-portions:

registered namespace package portions
*************************************

the following list contains all registered portions of the {namespace_name} namespace, plus additional modules of each
portion.


.. hint::
    a not on the ordering: portions with no dependencies are at the begin of the following list.
    the portions that are depending on other portions of the {namespace_name} namespace
    are listed more to the end.


.. autosummary::
    :toctree: _autosummary
    :nosignatures:

    {portions_import_names}


{manuals_include}


indices and tables
******************

* `portion repositories at {repo_domain} <{repo_root}>`__
* :ref:`genindex`
* :ref:`modindex`
* ``ae`` namespace `projects <https://gitlab.com/ae-group>`__ and `documentation <https://ae.readthedocs.io>`__
* ``aedev`` namespace `projects <https://gitlab.com/aedev-group>`__ and `documentation <https://aedev.readthedocs.io>`__
