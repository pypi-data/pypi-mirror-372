# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['sema4ai',
 'sema4ai.action_server',
 'sema4ai.action_server._preload_actions',
 'sema4ai.action_server._robo_utils',
 'sema4ai.action_server.env',
 'sema4ai.action_server.mcp',
 'sema4ai.action_server.migrations',
 'sema4ai.action_server.package',
 'sema4ai.action_server.vendored_deps',
 'sema4ai.action_server.vendored_deps.action_package_handling',
 'sema4ai.action_server.vendored_deps.package_deps',
 'sema4ai.action_server.vendored_deps.package_deps.conda_impl',
 'sema4ai.action_server.vendored_deps.package_deps.pip_impl',
 'sema4ai.action_server.vendored_deps.termcolors']

package_data = \
{'': ['*'], 'sema4ai.action_server': ['bin/*']}

install_requires = \
['aiohttp>=3.11.16,<4.0.0',
 'cryptography>=44.0.1,<45.0.0',
 'fastapi-slim>=0.116.1,<0.117.0',
 'jsonschema-specifications>=2024.10.1,<2025.0.0',
 'jsonschema>=4.23.0,<5.0.0',
 'mcp>=1.10.0,<2.0.0',
 'msgspec>=0.18,<0.19',
 'psutil>=5.0,<7.0',
 'pydantic>=2.9.2,<3.0.0',
 'pyyaml>=6,<7',
 'requests>=2,<3',
 'requests_oauthlib>=2.0,<3.0',
 'sema4ai-actions>=1.4.2,<2.0.0',
 'sema4ai-common>=0.2.1,<0.3.0',
 'termcolor>=2.4.0,<3.0.0',
 'uvicorn>=0.34.0,<0.35.0',
 'watchfiles>=0.24.0,<0.25.0',
 'websockets>=13.1,<14.0']

entry_points = \
{'console_scripts': ['action-server = sema4ai.action_server.cli:main']}

setup_kwargs = {
    'name': 'sema4ai-action-server',
    'version': '2.14.2',
    'description': 'Sema4AI Action Server',
    'long_description': "# sema4ai-action-server\n\n[Sema4.ai Action Server](https://github.com/sema4ai/actions#readme) is a Python framework designed to provide your Python functions to AI Agents. It works both as an MCP Server (hosting tools, resources and prompts) and also provides an OpenAPI compatible API.\n\nA `tool` or `action` in this case is defined as a Python function (which has inputs/outputs defined), which is served by the `Sema4.ai Action Server`.\n\nThe `Sema4.ai Action Server` automatically provides a `/mcp` endpoint for connecting `MCP` clients and also generates an OpenAPI spec for your Python code, enabling different AI/LLM Agents to understand and call your Action. It also manages the Action lifecycle and provides full traceability of what happened during any tool or action call (open the `/runs` endpoint in a browser to see not only inputs and output, but also a full `log.html` with internal details, such as variables and function calls that your Python function executed).\n\n## 1. Install Action Server\n\nAction Server is available as a stand-alone fully signed executable and via `pip install sema4ai-action-server`.\n\n> We recommend the executable to prevent confusion in case you have multiple/crowded Python environments, etc.\n\n#### For macOS\n\n```sh\n# Install Sema4.ai Action Server\nbrew update\nbrew install sema4ai/tools/action-server\n```\n\n#### For Windows\n\n```sh\n# Download Sema4.ai Action Server\ncurl -o action-server.exe https://cdn.sema4.ai/action-server/releases/latest/windows64/action-server.exe\n\n# Add to PATH or move to a folder that is in PATH\nsetx PATH=%PATH%;%CD%\n```\n\n#### For Linux\n\n```sh\n# Download Sema4.ai Action Server\ncurl -o action-server https://cdn.sema4.ai/action-server/releases/latest/linux64/action-server\nchmod a+x action-server\n\n# Add to PATH or move to a folder that is in PATH\nsudo mv action-server /usr/local/bin/\n```\n\n## 2. Run your first MCP tool\n\n```sh\n# Bootstrap a new project using this template.\n# You'll be prompted for the name of the project (directory):\naction-server new\n\n# Start Action Server\ncd my-project\naction-server start\n```\n\n👉 You should now have an Action Server running locally at: [http://localhost:8080](http://localhost:8080), so open that in your browser and the web UI will guide you further.\n\n## What do you need in your Action Package\n\nAn `Action Package` is currently defined as a local folder that contains at least one Python file containing an action entry point (a Python function marked with `@action` -decorator from `sema4ai.actions`).\n\nThe `package.yaml` file is required for specifying the Python environment and dependencies for your Action ([RCC](https://github.com/robocorp/rcc/) will be used to automatically bootstrap it and keep it updated given the `package.yaml` contents).\n\n> Note: the `package.yaml` is optional if the action server is not being used as a standalone (i.e.: if it was pip-installed it can use the same python environment where it's installed).\n\n### Bootstrapping a new Action\n\nStart new projects with:\n\n`action-server new`\n\nNote: the `action-server` executable should be automatically added to your python installation after `pip install sema4ai-action-server`, but if for some reason it wasn't pip-installed, it's also possible to use `python -m sema4ai.action_server` instead of `action-server`.\n\nAfter creating the project, it's possible to serve the actions under the current directory with:\n\n`action-server start`\n\nFor example: When running `action-server start`, the action server will scan for existing actions under the current directory, and it'll start serving those.\n\nAfter it's started, it's possible to access the following URLs:\n\n- `/index.html`: UI for the Action Server.\n- `/openapi.json`: Provides the openapi spec for the action server.\n- `/docs`: Provides access to the APIs available in the server and a UI to test it.\n\n## Documentation\n\nExplore our [docs](https://github.com/sema4ai/actions/tree/master/action_server/docs) for extensive documentation.\n\n## Changelog\n\nA list of releases and corresponding changes can be found in the [changelog](https://github.com/sema4ai/actions/blob/master/action_server/docs/CHANGELOG.md).\n",
    'author': 'Fabio Z.',
    'author_email': 'fabio@robocorp.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/sema4ai/actions/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.12,<3.14',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
