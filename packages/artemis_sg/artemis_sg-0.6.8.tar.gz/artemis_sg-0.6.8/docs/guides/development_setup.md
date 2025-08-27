# Setup Development Environment
In order to contribute to the development of this project, it is helpful to have
the tools used to manage, validate, test, and build the code.

This guide will walk through how to setup a development environment.

## Windows
This portion of the guide will walk through the setup of a development
environment on Windows.

Assumptions:
* PowerShell is installed.
* You are familiar with installing your editor/IDE of choice.

```{note}
These instructions have been derived from a detailed python
development environemt guide at [realpython.com][realpython_windows].
```

### Install Windows Terminal
Windows terminal will be used to display PowerShell sessions.  It is
recommended for displaying the prompt that will be provided by Oh My Posh.

Go to the
[Microsoft Windows Terminal web page][windowsterminal]
and follow the instructions for installing
Windows Terminal.

### Install Chocolatey
Chocolatey is a package management tool for Windows.  It makes it easy to
install and update the software packages that you use on your Windows device.

* Open an [Administrative PowerShell][admin_powershell] session.  Chocolatey
  should be installed using administrator privileges.

* Set execution policy to RemotedSigned to enable the installation.
```powershell
Set-ExecutionPolicy RemoteSigned
```
* Install Chocolatey
```powershell
iwr -useb community.chocolatey.org/install.ps1 | iex
```
* After the installation is complete, run the following command to verify it
  is installed properly.
```powershell
choco -?
```
* Close the administrative PowerShell instance.

### Install Supporting Software Tools
* Open a PowerShell session.

Run the following commands to install the recommended tools.
```powershell
choco install python --yes
choco install googlechrome --yes
choco install git --yes
choco install oh-my-posh --yes
choco install vim --yes  # or your editor of choice
```

Now, refresh the environment to update the `$PATH` to allow
access to the newly install software commands.
```powershell
refreshenv
```

### Configure Terminal for Oh My Posh
Here we will install a Nerd Font and configure Windows Terminal
to use it in order to display the glyphs used by the default
Oh My Posh theme.

* Install meslo nerd font.  See [Oh My Posh][ohmyposh_fonts] for more detail
  if needed.
```powershell
oh-my-posh font install meslo
```

* Set Windows Terminal default profile font to MesloLGM Nerd Font.

Type `CTRL+SHIFT+,` to open the Windows Terminal `settings.json` file.
Add the following font definition to the `profiles.defaults` entry.  Then
save the `settings.json` file.  You should see output in the PowerShell session
indicating that the fonts in this family have been loaded.
```powershell
"font": { "face": "MesloLGM Nerd Font" }
```

* Add oh-my-posh to your profile by adding the following line to your `$PROFILE`
  file.
```powershell
oh-my-posh init pwsh | Invoke-Expression
```

Reload your profile with the following command.
```powershell
. $PROFILE
```

Your prompt should now be that of the default Oh My Posh theme.


## Setup Artemis Python Development Environment
We will now setup a development checkout for the [artemis_sg][artemis_sg]
project.

### Create Python Virtual Environment
Create a python virtual environment for this development environment.
You may create this wherever you store python virtual environments on your
system.

If you don't currently manage python virtual environments, make a directory
for them in your `$HOME` folder.

```{tab} Windows
    cd "$HOME"
    md python_venvs
```

```{tab} Linux
    cd "$HOME"
    mkdir python_venvs
```

Create a python virtual environment named `venv_artemis_dev` for this
environment and then activate it.

```{tab} Windows Powershell
    cd "$HOME\python_venvs"
    py -m venv venv_artemis_dev
    .\venv_artemis_dev\Scripts\Activate.ps1
    python -m pip install --upgrade pip
```

```{tab} Linux
    cd "$HOME/python_venvs"
    python3 -m venv venv_artemis_dev
    source venv_artemis_dev/bin/activate
    python -m pip install --upgrade pip
```

### Clone Git Repository
We will now clone the git repository to get a local copy to work on.

If you do not have your own fork of the project, use the canonical
source of the repository.  If you do have your own fork, use the
URL appropriate for your forked copy.

```
cd $HOME
git clone https://gitlab.com/johnduarte/artemis_sg.git
```

### Install Python Packages
We will now use `pip` to install the packages required to run the
validation, testing, and build tools.

First, change directories into the root of the `artemis_sg` git
checkout.
```{tab} Windows Powershell
    cd "$HOME\artemis_sg"
```

```{tab} Linux
    cd "$HOME/artemis_sg"
```

Now run the following commands to install the necessary build packages.  The
order in which these commands are run is important, so be sure to execute them
in the order shown below.
```
pip install hatch
pip install .[optional-dependencies]
pip install -e .
artemis_sg --help
```

### Validate Environment

#### Lint Source Code
To validate that the development environment is setup properly, use `hatch`
to validate the syntax of the source code.

```
hatch -v run lint
```

The following output should be presented.
```
Finished checking dependencies
cmd [1] | ruff check .
```

#### Test Source Code
Use `hatch`
to run the tests for the code.

```
hatch -v run test
```

Output similar to the following should be presented.
```
Finished checking dependencies
cmd [1] | pytest -m "not integration" tests
========================================================= test session starts ==========================================================
platform linux -- Python 3.11.2, pytest-7.4.2, pluggy-1.3.0
rootdir: /home/yourname/artemis_sg
configfile: pytest.ini
plugins: cov-4.1.0
collected 132 items / 9 deselected / 123 selected

...
```

```{note}
We use the command `hatch run test` rather than `hatch test`
in order omit integration tests from the test suite.
```

#### Build Package
Use `hatch`
to build a package from the source code.

```
hatch -v build
```

Output similar to the following should be presented.
```
[sdist]
Building `sdist` version `standard`
dist/artemis_sg-0.6.5.dev6.tar.gz

[wheel]
Building `wheel` version `standard`
dist/artemis_sg-0.6.5.dev6-py3-none-any.whl
```

#### Build Documentation
Use `hatch`
to build the documentation from the source code.

```
hatch -v run doc
```

Output similar to the following should be presented.
```
Finished checking dependencies
cmd [1] | sphinx-apidoc -o docs/api --module-first --no-toc --force src/artemis_sg
cmd [2] | sphinx-build --keep-going -n -T -b html docs public
Running Sphinx v7.2.6
...
build succeeded, 1 warning.

The HTML pages are in public.
```

<!-- prettier-ignore-start -->
[ms_ps_exec_policies]: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-7.2
[choco_install]: https://community.chocolatey.org/courses/installation/installing?method=installing-chocolatey#cmd
[admin_powershell]: https://www.howtogeek.com/742916/how-to-open-windows-powershell-as-an-admin-in-windows-10/
[windowsterminal]: https://apps.microsoft.com/detail/9n0dx20hk701?ocid=webpdpshare
[ohmyposh_fonts]: https://ohmyposh.dev/docs/installation/fonts
[ohmyposh_prompt]: https://ohmyposh.dev/docs/installation/prompt
[artemis_sg]: https://gitlab.com/johnduarte/artemis_sg.git
[realpython_windows]: https://realpython.com/python-coding-setup-windows
<!-- prettier-ignore-end -->
