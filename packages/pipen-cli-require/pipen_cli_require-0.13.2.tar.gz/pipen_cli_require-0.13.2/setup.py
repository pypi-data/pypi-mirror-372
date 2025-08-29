# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pipen_cli_require']

package_data = \
{'': ['*']}

install_requires = \
['pipen-annotate>=0.15,<0.16']

entry_points = \
{'pipen_cli': ['cli-require = pipen_cli_require:PipenCliRequirePlugin']}

setup_kwargs = {
    'name': 'pipen-cli-require',
    'version': '0.13.2',
    'description': 'A pipen cli plugin to check requirements for processes of a pipeline',
    'long_description': '# pipen-cli-require\n\nChecking the requirements for processes of a [pipen][1] pipeline\n\n## Install\n\n```shell\npip install -U pipen-cli-require\n```\n\n## Usage\n\n### Defining requirements of a process\n\n```python\n# example_pipeline.py\nfrom pipen import Pipen, Proc\n\nclass P1(Proc):\n    """Process 1\n\n    Requires:\n        pipen: Run `pip install -U pipen` to install\n          - check: |\n            {{proc.lang}} -c "import pipen"\n        liquidpy: Run `pip install -U liquidpy` to install\n          - check: |\n            {{proc.lang}} -c "import liquid"\n        nonexist: Run `pip install -U nonexist` to install\n          - check: |\n            {{proc.lang}} -c "import nonexist"\n        conditional:\n          - if: {{envs.require_conditional}}\n          - check:\n            {{proc.lang}} -c "import optional"\n\n    """\n    input = "a"\n    output = "outfile:file:out.txt"\n    envs = {"require_conditional": False}\n    lang = "python"\n\n# Setup the pipeline\n# Must be outside __main__\n# Or define a function to return the pipeline\nclass Pipeline(Pipen):\n    starts = P1\n\n\nif __name__ == \'__main__\':\n    # Pipeline must run with __main__\n    Pipeline().run()\n```\n\n### Parsing process requirements using API\n\n```python\nfrom pipen_cli_require import parse_proc_requirements\n\n\ndef parse_proc_requirements(\n    proc: Type[Proc]\n) -> Tuple[OrderedDiot, OrderedDiot]:\n    """Parse the requirements of a process\n\n    Args:\n        proc: The process class\n\n    Returns:\n        A tuple of two OrderedDiot\'s.\n        The first one is the annotated sections by pipen_annotate\n        The second one is the requirements. The key is the name of the\n            requirement, the value is a dict with message, check and if_ keys.\n    """\n```\n\n## Checking the requirements via the CLI\n\n```shell\n> pipen require --verbose --ncores 2 -p example_pipeline.py:pipeline\n\nChecking requirements for pipeline: PIPEN-0\n│\n└── P1: Process 1\n    ├── ✅ pipen\n    ├── ✅ liquidpy\n    ├── ❎ nonexist: Run `pip install -U nonexist` to install\n    │   └── Traceback (most recent call last):\n    │         File "<string>", line 1, in <module>\n    │       ModuleNotFoundError: No module named \'nonexist\'\n    │\n    └── ⏩ conditional (skipped by if-statement)\n```\n\n## Checking requirements with runtime arguments\n\nFor example, when I use a different python to run the pipeline:\n\nAdd this to the head of `example_pipeline.py`:\n\n```python\nimport pipen_args\n```\n\nSee also `tests/pipen_args_pipeline.py`\n\nThen specify the path of the python to use:\n\n```shell\npipen require example_pipeline.py:pipeline --P1.lang /path/to/another/python\n```\n\n[1]: https://github.com/pwwang/pipen\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
