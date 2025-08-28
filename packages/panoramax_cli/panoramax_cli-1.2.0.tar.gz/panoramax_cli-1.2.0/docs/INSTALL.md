# Install

Panoramax CLI can be installed using various methods:

- :simple-python: From [PyPI](https://pypi.org/project/panoramax_cli/), the Python central package repository
- :package: From packaged binaries for Windows & Linux, availaible in the [latest release page](https://gitlab.com/panoramax/clients/cli/-/releases/)
- :simple-git: Using this [Git repository](https://gitlab.com/panoramax/clients/cli)

Panoramax CLI is compatible with all Python versions >= 3.9.

!!! tip

	If your system does not support python 3.9, you can use a tool like [pyenv](https://github.com/pyenv/pyenv) or [uv](https://docs.astral.sh/uv/guides/install-python/#installing-a-specific-version) to install a newer python version.


=== ":fontawesome-brands-windows: Windows"

	On Windows, just download the [latest Windows executable](https://gitlab.com/panoramax/clients/cli/-/releases/permalink/latest/downloads/bin/panoramax_cli-win-amd64.exe) and open a shell in the download directory (you can do that by typing `cmd` in the explorer opened in the directory).

	Then, simply run:

	```powershell
	panoramax_cli-win-amd64.exe --help
	```

=== ":simple-linux: Linux"

	!!! note
		Linux binary has been built for AMD64. They are built using Ubuntu 22.04, so they should work for all newer versions. For older version though, there might be _libstdc++_ incompatibilities; if you encounter that problem, you can update libstdc++ or install using _PyPi_.

	Download the [latest Linux binary](https://gitlab.com/panoramax/clients/cli/-/releases/permalink/latest/downloads/bin/panoramax_cli-linux-amd64), then in the download directory:

	```bash
	chmod u+x panoramax_cli-linux-amd64
	./panoramax_cli-linux-amd64 --help
	```

	Optionally, you can put this in /usr/local/bin (if it's in your path) for a simpler use:

	```bash
	chmod u+x panoramax_cli-linux-amd64
	mv panoramax_cli-linux-amd64 /usr/local/bin/panoramax_cli

	panoramax_cli --help
	```

=== ":simple-pypi: PyPI"

	Just run this command:

	```bash
	pip install panoramax_cli
	```

	You should then be able to use the CLI tool with the name `panoramax_cli`:

	```bash
	panoramax_cli --help
	```

	Alternatively, you can use [pipx](https://github.com/pypa/pipx) if you want all the script dependencies to be in a custom virtual env.

	If you choose to [install pipx](https://pypa.github.io/pipx/installation/), then run:

	```bash
	pipx install panoramax_cli
	```

=== ":simple-uv: Python package with uv"

	[uv](https://docs.astral.sh/uv/) is a really efficient tool to handle python programs.

	You just need to install uv, following [their documentation](https://docs.astral.sh/uv/getting-started/installation/).

	Then you can just run:

	```bash
	uvx panoramax_cli --help
	```

	It will handle the installation of the python package, the virtual env and will run `panoramax_cli`.

=== ":simple-git: Git"

	Download the repository:

	```bash
	git clone https://gitlab.com/panoramax/clients/cli.git panoramax_cli
	cd panoramax_cli/
	```

	To avoid conflicts, it's considered a good practice to create a _[virtual environment](https://docs.python.org/3/library/venv.html)_ (or virtualenv). To do so, launch the following commands:

	```bash
	# Create the virtual environment in a folder named "env"
	python3 -m venv env

	# Launches utilities to make environment available in your Bash
	source ./env/bin/activate
	```

	Then, install the Panoramax CLI dependencies using pip:

	```bash
	pip install -e .
	```

	You can also install the `dev` and `docs` dependencies if necessary (to have lints, format, tests...):

	```bash
	pip install -e .[dev,docs]
	```

	Then, you can use the `panoramax_cli` command:

	```bash
	panoramax_cli --help
	```

!!! note
	Panoramax CLI has had numerous changes since its version 1.0.0, which makes it compatible only with API supporting _Upload Set_ system for sending pictures. Panoramax API starts supporting Upload Set on version 2.7. If you're working with an older Panoramax API, or using a third-party STAC API not compatible with Upload Sets, you can use older version of CLI:

	```bash
	pip install panoramax_cli=0.3.13
	```

	However, it's better to encourage all API administrators to move to a recent Panoramax API version, or make their third-party API compatible with Upload Sets.

## Updating an existing installation

Updating `panoramax_cli` depends on the installation method:

=== ":fontawesome-brands-windows: Windows"

	On Windows, just download the [latest Windows executable](https://gitlab.com/panoramax/clients/cli/-/releases/permalink/latest/downloads/bin/panoramax_cli-win-amd64.exe) and open a shell in the download directory (you can do that by typing `cmd` in the explorer opened in the directory).

	!!! warning
		If there was a previous executable in the directory, make sure to rename or delete the old `panoramax_cli-win-amd64.exe` file. Else the new file might be named like `panoramax_cli-win-amd64(1).exe`

	Then, simply run:

	```powershell
	panoramax_cli-win-amd64.exe --help
	```

=== ":simple-linux: Linux"

	Download the [latest Linux binary](https://gitlab.com/panoramax/clients/cli/-/releases/permalink/latest/downloads/bin/panoramax_cli-linux-amd64).

	!!! warning
		If there was a previous executable in the directory, make sure to rename or delete the old `panoramax_cli-linux-amd64` file. Else the new file might be named like `panoramax_cli-linux-amd64(1) 
	
	Then in the download directory:
	
	```bash
	chmod u+x panoramax_cli-linux-amd64
	./panoramax_cli-linux-amd64 --help
	```

	Optionally, you can put this in /usr/local/bin (if it's in your path) for a simpler use:

	```bash
	chmod u+x panoramax_cli-linux-amd64
	mv panoramax_cli-linux-amd64 /usr/local/bin/panoramax_cli

	panoramax_cli --help
	```

=== ":simple-pypi: PyPI"

	Just run this command:

	```bash
	pip install --upgrade panoramax_cli
	```

	!!! warning
		If you previously used `geovisio_cli` (older versions with older name), make sure to uninstall it first with `pip uninstall geovisio_cli`. Also, as the CLI was renamed, make sure to update your own scripts if you have any to use the new executable name `panoramax_cli` (instead of `geovisio`).


=== ":simple-uv: Python package with uv"

	With [uv](https://docs.astral.sh/uv/) updating the package is as simple as:

	```bash
	uvx panoramax_cli@latest --help
	```

	It will handle the installation and update of the python package, the virtual env and will run `panoramax_cli`.

=== ":simple-git: Git"

	In the previously cloned git repository `panoramax_cli`, update the sources:

	```bash
	git pull --rebase
	```

	Activate the virtual env:

	```bash
	source ./env/bin/activate
	```

	Then, install the Panoramax CLI dependencies using pip:

	```bash
	pip install --upgrade -e .
	```
