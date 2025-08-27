# Installation
You need [Python](https://python.org/downloads) 3.7 or greater and the
[pip package management tool](https://pip.pypa.io/en/stable/installation)
installed.

## Setup Python Environment
It is recommended to create a python virtual environment for this application.
You may create this wherever you store python virtual environments on your
system.

If you don't currently manage python virtual environments, make a directory
for them in your $HOME folder.

```{tab} Windows
    cd "$HOME"
    md python_venvs
```

```{tab} Linux
    cd "$HOME"
    mkdir python_venvs
```

Create a python virtual environment named `venv_artemis` for this
application and then activate it.  With the environment activated,
install the `artemis_sg` package to enable the CLI.

```{tab} Windows Powershell
    cd "$HOME\python_venvs"
    py -m venv venv_artemis
    .\venv_artemis\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install artemis_sg
```

```{tab} Windows CMD
    cd "$HOME\python_venvs"
    py -m venv venv_artemis
    .\venv_artemis\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install artemis_sg
```

```{tab} Linux
    cd "$HOME/python_venvs"
    python3 -m venv venv_artemis
    source venv_artemis/bin/activate
    python -m pip install --upgrade pip
    pip install artemis_sg
```

## Google API
The Google API client library for Python is required.
See the
[Google Slides API Quickstart](https://developers.google.com/slides/api/quickstart/python)
for instructions on setting up API authorization.

***Important:***
The setup above will produce a `credentials.json` file needed to authenticate
to the Google Slides and Sheet API.
The application will not work as expected unless the `credentials.json`
location is properly defined in the `config.toml` file for the application.
See the instruction under {ref}`Setup Configuration` for defining of this location.


## Google Cloud
Using Google Cloud Storage requires a private service account key as an
authentication mechanism.
Signed URLs will be generated to put the images into the slides.  This
requires a service account and service account key file.

### Enable Google Cloud Storage API
* In the Google Cloud account dashboard, click 'APIs & Services' from the
  navigation menu.
* Click '+ ENABLE APIS AND SERVICES'
* Search for 'cloud storage'
* Enable Google Cloud Storage JSON API
* Enable Google Cloud Storage

### Create Service Account
* In the Google Cloud account dashboard, select 'APIs & Services' from the
  navigation menu.  Then click 'Credentials' in the sub-menu.
* Click '+ CREATE CREDENTIALS'
* Choose 'Service Account' from the drop-down menu.
* Name the account and click 'Create'.
* Choose 'Owner' from the 'Basic' roll in the 'Grant access' section.
* Click 'Continue'
* Click 'Done'

### Create Service Account Key
* Open the service account from the Credentials list in the Google Cloud
  account.
* Click 'KEYS'
* Click 'ADD KEY'
* Click 'CREATE NEW KEY'
* Choose JSON format
* Click 'CREATE'
* Save the key.
* Modify the file permissions on the key to make it READ-ONLY.

***Important:***
The application will not work as expected unless the Google
Cloud key location is properly defined in the `config.toml` file for the application.
See the instructions under {ref}`Setup Configuration`
for defining this location.

## Setup Configuration

### Directories
The application uses local user directories to store its configuration and
data.  They are defined by a combination of the Operating System and user.
Here are the patterns that they follow.

```{tab} Windows
    $user_data_dir='C:\\Users\\USERNAME\\AppData\\Local\\artemis_sg'
    $user_config_dir='C:\\Users\\USERNAME\\AppData\\Local\\artemis_sg'
```

```{tab} Linux
    user_data_dir='/home/USERNAME/.local/share/artemis_sg'
    user_config_dir='/home/USERNAME/.config/artemis_sg'
```

### Creating The Configuration Skeleton
When you first run the application, a skeleton of everything you need for
configuration will be created.  Run the following command to set up the
skeleton.

```sh
artemis_sg --help
```

### Update `config.toml`
All of the needed configuration keys have been created for you in the
`$user_config_dir/config.toml` file.  Some of the fields in this file
*must* be updated in order for the application to operate as expected.

Open the `config.toml` file in your favorite plain text editor and update
the fields in the following sections.

*NOTE*: All string values should be contained in double quotes.

#### Update google.cloud
All of the fields in the `[google.cloud]` section need to be updated to
match your Google Cloud Storage account setup.

* `bucket`: The name of the Google Cloud Storage Bucket that the application
  will use to upload/download files.
* `bucket_prefix`: The prefix name within the Google Cloud Storage Bucket
  (a.k.a folder name) that the application will use to upload/download image
  files.
* `public_html_bucket`: The name of the public Google Cloud Storage Bucket that the application will use to upload html slide decks.
* `key_file`: The local file path of the Google Cloud Key created in the
  {ref}`Create Service Account Key` section.  This
  should be the full absolute path to the key file.  By default, this is set
  to be in the `$user_data_dir`.  You can leave this field value as is and
  copy the Google Cloud Service Account Key file to the location defined in
  this field.
* Copy the Google Cloud Service Account Key file to the application data
  directory as shown in the `google.cloud.key_file` field value.
* Modify the file permissions on the key file to make it READ-ONLY.

#### Update google.docs
None of the fields need to be updated.  However, you will now need to copy
the `credentials.json` file created in the {ref}`Google API` section
to the path shown for the `api_creds_file` field.

* Copy the `credentials.json` file to the application data directory as shown
  in the `api_creds_file` field value.
* Modify the file permissions on the token to make it READ-ONLY.

## Final Setup Checklist
Once you have completed all of the above setup {ref}`Installation` steps, run
through the following checklist to make sure you are ready to proceed.

* Google API `credentials.json` is located in the [application data directory](#directories).
* `config.toml` has been updated with valid values for the following:
    * `google.cloud.bucket` - This should be set to a valid cloud bucket.
    * `google.cloud.bucket_prefix` - This should be set to a valid cloud bucket prefix.
    * `google.cloud.key_file` - This should be set to the name of your Service key file.
* `artemis_sg --help` - results in usage text showing the defined subcommands.

## Upgrade
To upgrade to the latest release, use pip.
```
pip install artemis_sg --upgrade
```
