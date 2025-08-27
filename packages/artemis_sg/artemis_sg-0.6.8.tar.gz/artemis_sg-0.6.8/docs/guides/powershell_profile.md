# PowerShell Profile
A PowerShell Profile can be used to simplify common tasks.

This guide will walk through how to create the profile and add an alias to it
in order to make activating your Python Virtual Environment easier.

To make it easier to activate your Python Environment in PowerShell,
you can define a function in your PowerShell `$PROFILE`.  In the example
below it is called `activate-venv-artemis`.

Assumptions:
* PowerShell is installed
* Python is installed
* A Python Virtual Environment named `venv_artemis` is set up.

## Enable Local Scripts
PowerShell execution policy needs to be updated in order to add scripts to be
run.  We will set the policy to allow locally created scripts but deny
execution for scripts downloaded from the internet.

See [Microsoft PowerShell Execution Policies][ms_ps_exec_policies] for detailed
background.

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Ensure Profile
See if a PowerShell profile is defined:
```powershell
$PROFILE
```

The above will return `false` or a file path.  `false` means the profile is not
defined.  However, even if a file path is returned it may not exist yet.  Check
to see if the profile path exists.
```powershell
type $PROFILE
```

If the above returns a `type: cannot find path '<PATH>' because it does not
exist` error, then the profile file does not exist.

*Only if* the profile is not defined or the profile file does not exist, force
the creation of the profile file.
```powershell
ni -Force $PROFILE
```

## Create Profile Content
Find the full path to your `artemis_sg` python virtual environment activation
script.  If you have followed the {ref}`Installation` instructions, this path
will be `$HOME\python_venvs\venv_artemis\Scripts\Activate.ps1`.  We will create
a function name to run this script in the `$PROFILE` file.

Open the profile file in notepad
```powershell
notepad $PROFILE
```

Add the following content to your profile
```powershell
# Microsoft.PowerShell_profile.ps1

Set-Alias python-sys  $(py -c 'import sys; print(sys.executable)')

$USER_DATA_DIR="$HOME\\AppData\\Local\\artemis_sg"
$USER_CONFIG_DIR="$HOME\\AppData\\Local\\artemis_sg"

function activate-venv-artemis {
& $HOME\python_venvs\venv_artemis\Scripts\Activate.ps1
}
```

Restart your PowerShell session to load the updated profile.
```powershell
exit
powershell
```

## Activate the Artemis Python Virtual Environment
```powershell
activate-venv-artemis
```

<!-- prettier-ignore-start -->
[ms_ps_exec_policies]: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies?view=powershell-7.2
<!-- prettier-ignore-end -->
