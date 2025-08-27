# THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.project_tpls v0.3.49
""" setup of aedev namespace package portion app_tpls: aedev_app_tpls module main module. """
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
    'description': 'aedev namespace package portion app_tpls: aedev_app_tpls module main module',
    'extras_require': {       'dev': [       'aedev_project_tpls', 'aedev_aedev', 'anybadge', 'coverage-badge', 'aedev_git_repo_manager',
                       'flake8', 'mypy', 'pylint', 'pytest', 'pytest-cov', 'pytest-django', 'typing',
                       'types-setuptools', 'wheel', 'twine'],
        'docs': [],
        'tests': [       'anybadge', 'coverage-badge', 'aedev_git_repo_manager', 'flake8', 'mypy', 'pylint', 'pytest',
                         'pytest-cov', 'pytest-django', 'typing', 'types-setuptools', 'wheel', 'twine']},
    'install_requires': [],
    'keywords': ['configuration', 'development', 'environment', 'productivity'],
    'license': 'GPL-3.0-or-later',
    'long_description': ('<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.aedev v0.3.26 -->\n'
 '<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.namespace_root_tpls v0.3.18 -->\n'
 '# app_tpls 0.3.18\n'
 '\n'
 '[![GitLab develop](https://img.shields.io/gitlab/pipeline/aedev-group/aedev_app_tpls/develop?logo=python)](\n'
 '    https://gitlab.com/aedev-group/aedev_app_tpls)\n'
 '[![LatestPyPIrelease](\n'
 '    https://img.shields.io/gitlab/pipeline/aedev-group/aedev_app_tpls/release0.3.18?logo=python)](\n'
 '    https://gitlab.com/aedev-group/aedev_app_tpls/-/tree/release0.3.18)\n'
 '[![PyPIVersions](https://img.shields.io/pypi/v/aedev_app_tpls)](\n'
 '    https://pypi.org/project/aedev-app-tpls/#history)\n'
 '\n'
 '>aedev namespace package portion app_tpls: aedev_app_tpls module main module.\n'
 '\n'
 '[![Coverage](https://aedev-group.gitlab.io/aedev_app_tpls/coverage.svg)](\n'
 '    https://aedev-group.gitlab.io/aedev_app_tpls/coverage/index.html)\n'
 '[![MyPyPrecision](https://aedev-group.gitlab.io/aedev_app_tpls/mypy.svg)](\n'
 '    https://aedev-group.gitlab.io/aedev_app_tpls/lineprecision.txt)\n'
 '[![PyLintScore](https://aedev-group.gitlab.io/aedev_app_tpls/pylint.svg)](\n'
 '    https://aedev-group.gitlab.io/aedev_app_tpls/pylint.log)\n'
 '\n'
 '[![PyPIImplementation](https://img.shields.io/pypi/implementation/aedev_app_tpls)](\n'
 '    https://gitlab.com/aedev-group/aedev_app_tpls/)\n'
 '[![PyPIPyVersions](https://img.shields.io/pypi/pyversions/aedev_app_tpls)](\n'
 '    https://gitlab.com/aedev-group/aedev_app_tpls/)\n'
 '[![PyPIWheel](https://img.shields.io/pypi/wheel/aedev_app_tpls)](\n'
 '    https://gitlab.com/aedev-group/aedev_app_tpls/)\n'
 '[![PyPIFormat](https://img.shields.io/pypi/format/aedev_app_tpls)](\n'
 '    https://pypi.org/project/aedev-app-tpls/)\n'
 '[![PyPILicense](https://img.shields.io/pypi/l/aedev_app_tpls)](\n'
 '    https://gitlab.com/aedev-group/aedev_app_tpls/-/blob/develop/LICENSE.md)\n'
 '[![PyPIStatus](https://img.shields.io/pypi/status/aedev_app_tpls)](\n'
 '    https://libraries.io/pypi/aedev-app-tpls)\n'
 '[![PyPIDownloads](https://img.shields.io/pypi/dm/aedev_app_tpls)](\n'
 '    https://pypi.org/project/aedev-app-tpls/#files)\n'
 '\n'
 '\n'
 '## installation\n'
 '\n'
 '\n'
 'execute the following command to install the\n'
 'aedev.app_tpls package\n'
 'in the currently active virtual environment:\n'
 ' \n'
 '```shell script\n'
 'pip install aedev-app-tpls\n'
 '```\n'
 '\n'
 'if you want to contribute to this portion then first fork\n'
 '[the aedev_app_tpls repository at GitLab](\n'
 'https://gitlab.com/aedev-group/aedev_app_tpls "aedev.app_tpls code repository").\n'
 'after that pull it to your machine and finally execute the\n'
 'following command in the root folder of this repository\n'
 '(aedev_app_tpls):\n'
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
 'https://gitlab.com/aedev-group/aedev_app_tpls/-/blob/develop/CONTRIBUTING.rst)\n'
 '\n'
 '\n'
 '## namespace portion documentation\n'
 '\n'
 'information on the features and usage of this portion are available at\n'
 '[ReadTheDocs](\n'
 'https://aedev.readthedocs.io/en/latest/_autosummary/aedev.app_tpls.html\n'
 '"aedev_app_tpls documentation").\n'),
    'long_description_content_type': 'text/markdown',
    'name': 'aedev_app_tpls',
    'package_data': {       '': [       'templates/de_tpl_main.py', 'templates/requirements.txt', 'templates/de_tpl_buildozer.spec',
                    'templates/main.kv', 'templates/de_mtp_snd/filter_on.wav', 'templates/de_mtp_snd/filter_off.wav',
                    'templates/de_mtp_img/app_icon.png', 'templates/de_mtp_img/access_right_x.png',
                    'templates/de_mtp_img/access_right_C.png', 'templates/de_mtp_img/open_userz_access.png',
                    'templates/de_mtp_img/access_right_U.png', 'templates/de_mtp_img/access_right_D.png',
                    'templates/de_mtp_img/access_right_r.png', 'templates/de_mtp_img/app_icon.jpg',
                    'templates/de_mtp_img/light_1/app_icon.png', 'templates/de_mtp_img/light_1/access_right_x.png',
                    'templates/de_mtp_img/light_1/access_right_C.png',
                    'templates/de_mtp_img/light_1/open_userz_access.png',
                    'templates/de_mtp_img/light_1/access_right_U.png',
                    'templates/de_mtp_img/light_1/access_right_D.png',
                    'templates/de_mtp_img/light_1/access_right_r.png',
                    'templates/de_mtp_ae_updater_moves/{project_name}.ini',
                    'templates/de_mtp_ae_updater_moves/FStringEvalSuggestions.txt', 'templates/de_mtp_loc/es/Msg.txt',
                    'templates/de_mtp_loc/de/Msg.txt', 'templates/de_mtp_loc/en/Msg.txt', 'templates/main.kv']},
    'packages': [       'aedev.app_tpls', 'aedev.app_tpls.templates', 'aedev.app_tpls.templates.de_mtp_snd',
        'aedev.app_tpls.templates.de_mtp_img', 'aedev.app_tpls.templates.de_mtp_ae_updater_moves',
        'aedev.app_tpls.templates.de_mtp_loc', 'aedev.app_tpls.templates.de_mtp_img.light_1',
        'aedev.app_tpls.templates.de_mtp_loc.es', 'aedev.app_tpls.templates.de_mtp_loc.de',
        'aedev.app_tpls.templates.de_mtp_loc.en'],
    'project_urls': {       'Bug Tracker': 'https://gitlab.com/aedev-group/aedev_app_tpls/-/issues',
        'Documentation': 'https://aedev.readthedocs.io/en/latest/_autosummary/aedev.app_tpls.html',
        'Repository': 'https://gitlab.com/aedev-group/aedev_app_tpls',
        'Source': 'https://aedev.readthedocs.io/en/latest/_modules/aedev/app_tpls.html'},
    'python_requires': '>=3.9',
    'setup_requires': [],
    'url': 'https://gitlab.com/aedev-group/aedev_app_tpls',
    'version': '0.3.18',
    'zip_safe': False,
}

if __name__ == "__main__":
    setuptools.setup(**setup_kwargs)
    pass
