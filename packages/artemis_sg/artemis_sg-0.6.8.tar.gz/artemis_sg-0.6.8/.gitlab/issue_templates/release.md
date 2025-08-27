# Release

## Release Scope

Placeholder for items in scope for release.

- Item One

## Release Checklist

## Main Release

There is no set release schedule.  Main releases are conducted when main
release [milestones](https://gitlab.com/johnduarte/artemis_sg/-/milestones)
are completed.

* [ ] Open a release issue.  Example [#168](https://gitlab.com/johnduarte/artemis_sg/-/issues/168).
    * [ ] Add items under *Release Scope* that will be part of the release from the *Unreleased* section of `CHANGELOG.md`.
* [ ] Merge development branch to `main` branch and push
* [ ] Check [pipeline](https://gitlab.com/johnduarte/artemis_sg/-/pipelines?ref=main) to confirm passing tests in `main` branch.
* [ ] Check [pages](https://johnduarte.gitlab.io/artemis_sg/) to confirm documentation is in order on `main` branch.
* [ ] Build test packages:
```bash
hatch build
hatch publish -r test -u __token__ -a pypi-<SECRET_TOKEN>
```
* [ ] Perform acceptance testing on Windows 11 and Debian 12 using test packages and ensure passing tests.
  * Ensure package is installed from [test.pypi.org](https://test.pypi.org/project/artemis_sg/) e.g:
```
asg_pkg_ver=0.0.0.dev0
pip install -i https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple \
    artemis_sg==$asg_pkg_ver
```

  * Vagrantfile for Windows 11

<p>
<details>
<summary>Click this to collapse/fold.</summary>

<pre><code>

# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "gusztavvargadr/windows-11"
  config.vm.communicator = "winrm"
  config.winrm.port = 55985
  config.vm.provision "shell", inline: <<-POWERSHELL
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    choco install python --yes
    choco install git --yes
    choco install sed --yes
    choco install vim --yes
    choco install googlechrome --yes
    choco install chromedriver --yes
  POWERSHELL
  config.vm.provision "shell", privileged: false, inline: <<-POWERSHELL
    md C:\\users\\vagrant\\python_venvs
    cd C:\\users\\vagrant\\python_venvs
    py -m venv venv_artemis
    .\\venv_artemis\\Scripts\\activate.ps1
    python -m pip install --upgrade pip
    pip install -i https://test.pypi.org/simple/ \
      --extra-index-url https://pypi.org/simple \
      artemis_sg==#{ENV['ASG_PKG_VER']}
    artemis_sg --help
    $CONFIG_PATH="C:\\Users\\vagrant\\AppData\\Local\\artemis_sg\\config.toml"
    echo "Updating $CONFIG_PATH"
    sed -i '/^bucket = /c bucket = \\"gj_images\\"' $CONFIG_PATH
    sed -i '/^bucket_prefix = /c bucket_prefix = \\"artemis_images\\"' $CONFIG_PATH
    sed -i '/^key_file = /c key_file = \\"C:\\\\\\\\vagrant\\\\\\\\google_cloud_service_key.json\\"' $CONFIG_PATH
    sed -i '/^api_creds_file = /c api_creds_file = \\"C:\\\\\\\\vagrant\\\\\\\\credentials.json\\"' $CONFIG_PATH
    sed -i '/^api_creds_token = /c api_creds_token = \\"C:\\\\\\\\vagrant\\\\\\\\app_creds_token.json\\"' $CONFIG_PATH
    sed -i '/^headless = /c headless = true' $CONFIG_PATH
  POWERSHELL
end

</code></pre>

</details>
</p>

  * Vagrantfile for Debian 12

<p>
<details>
<summary>Click this to collapse/fold.</summary>

<pre><code>
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "debian/bookworm64"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "1024"
  end
  config.vm.provision "shell", inline: <<-SHELL
    # Install Google Chrome
    apt-get update
    apt-get install -y software-properties-common apt-transport-https ca-certificates curl
    curl -fSsL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor | tee /usr/share/keyrings/google-chrome.gpg >> /dev/null
    echo deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main | tee /etc/apt/sources.list.d/google-chrome.list
    apt-get update
    apt-get install -y google-chrome-stable
    apt-get install -y vim tree python3-pip python3-venv git
  SHELL
  config.vm.provision "shell", privileged: false, inline: <<-SHELL
    echo "set -o vi" >> $HOME/.bashrc
    echo "PATH=$PATH:$HOME/.local/bin" >> $HOME/.bashrc
    mkdir $HOME/python_venvs
    cd $HOME/python_venvs
    python3 -m venv venv_artemis
    source venv_artemis/bin/activate
    python -m pip install --upgrade pip
    pip install -i https://test.pypi.org/simple/ \
      --extra-index-url https://pypi.org/simple \
      artemis_sg==#{ENV['ASG_PKG_VER']}
    artemis_sg --help
    echo "Updating config.toml for vagrant user"
    CONFIG_PATH="$HOME/.config/artemis_sg/config.toml"
    sed -i '/^bucket = /c bucket = "gj_images"' $CONFIG_PATH
    sed -i '/^bucket_prefix = /c bucket_prefix = "artemis_images"' $CONFIG_PATH
    sed -i '/^key_file = /c key_file = "/vagrant/google_cloud_service_key.json"' $CONFIG_PATH
    sed -i '/^api_creds_file = /c api_creds_file = "/vagrant/credentials.json"' $CONFIG_PATH
    sed -i '/^api_creds_token = /c api_creds_token = "/vagrant/app_creds_token.json"' $CONFIG_PATH
    sed -i '/^headless = /c headless = true' $CONFIG_PATH
  SHELL
end

</code></pre>

</details>
</p>

  * Prepare vagrant boxen directories:
```
WIN11_VAGRANT_PATH=$HOME/tmp/vagrant/win11
DEB12_VAGRANT_PATH=$HOME/tmp/vagrant/deb12
echo $WIN11_VAGRANT_PATH $DEB12_VAGRANT_PATH | xargs -n 1 cp $HOME/.local/share/artemis_sg/google_cloud_service_key.json
echo $WIN11_VAGRANT_PATH $DEB12_VAGRANT_PATH | xargs -n 1 cp $HOME/.local/share/artemis_sg/credentials.json
echo $WIN11_VAGRANT_PATH $DEB12_VAGRANT_PATH | xargs -n 1 cp $HOME/.local/share/artemis_sg/app_creds_token.json
echo $WIN11_VAGRANT_PATH $DEB12_VAGRANT_PATH | xargs -n 1 cp $PWD/tests/data/test_sheet.xlsx
```
  * Spin up vagrant boxen with test package e.g.:
```
ASG_PKG_VER=0.0.0.dev0 vagrant up
```
  * Perform [generate workflow](https://johnduarte.gitlab.io/artemis_sg/usage.html#slide-generator-workflow)
    * From Google Sheet id
    *     artemis_sg -v sample -b "1ZTa1wAElGjSdEtsuDR6TwlxmOhJIFnvED5Dkl6klK40" scrape download upload generate -t "cool deck"
    * From Excel file
    *     artemis_sg -v sample -b C:\vagrant\test_sheet.xlsx scrape download upload generate -t "cool deck"
    *     artemis_sg -v sample -b /vagrant/test_sheet.xlsx scrape download upload generate -t "cool deck"
  * Perform [sheet-image workflow](https://johnduarte.gitlab.io/artemis_sg/usage.html#spreadsheet-images-workflow)
    *     artemis_sg -v sample -b C:\vagrant\test_sheet.xlsx  scrape download mkthumbs sheet-image -o C:\vagrant\out.xlsx
    *     artemis_sg -v sample -b /vagrant/test_sheet.xlsx  scrape download mkthumbs sheet-image -o /vagrant/out.xlsx
  * Perform [sheet-waves workflow](https://johnduarte.gitlab.io/artemis_sg/usage.html#spreadsheet-waves-workflow)
    *     artemis_sg -v sample -b C:\vagrant\test_sheet.xlsx  scrape sheet-waves -o C:\vagrant\out.xlsx
    *     artemis_sg -v sample -b /vagrant/test_sheet.xlsx  scrape sheet-waves -o /vagrant/out.xlsx
* [ ] Update `CHANGELOG.md`.
  * Move "Unreleased" section to pending to "version" section e.g. "0.7.0".
  * Create clean "Unreleased" section.
  * Add "version" compare link e.g. "0.7.0".
  * Update "unreleased" compare link.
* [ ] Create tag for release e.g.:
```bash
git tag --sign v0.7.0
# Title to match tag; Body should be bullet list from `CHANGELOG.md`.
git push origin v0.7.0
```
* [ ] Create packages e.g.:
```bash
git checkout v0.7.0
hatch build -c
hatch publish -r test -u __token__ -a pypi-<SECRET_TOKEN>
hatch publish -u __token__ -a pypi-<SECRET_TOKEN>
```
* [ ] [Create release on gitlab](https://gitlab.com/johnduarte/artemis_sg/-/releases/new)


## Point Release
Released as needed for security, installation or critical bug fixes.

* [ ] Open a release issue.  Example [#168](https://gitlab.com/johnduarte/artemis_sg/-/issues/168).
    * [ ] Add items under *Release Scope* that will be part of the release from the *Unreleased* section of `CHANGELOG.md`.
* [ ] Make necessary changes in `main` branch.
* [ ] Update `CHANGLOG.md`.
* [ ] Check out release branch e.g.:
```bash
git checkout -t remotes/origin/0.6.x
```
* Cherry-pick individual commits from `main` branch to release branch e.g. `0.6.x`, then `git push`.
* [ ] Check [pipeline](https://gitlab.com/johnduarte/artemis_sg/-/pipelines)
to confirm passing tests in release branch e.g. `0.6.x`.
* [ ] Check [pages](https://johnduarte.gitlab.io/artemis_sg/) to confirm documentation is in order on `main` branch (pages tied to main).
* [ ] Build test packages:
```bash
hatch build
hatch publish -r test -u __token__ -a pypi-<SECRET_TOKEN>
```
* [ ] Perform acceptance testing on Windows 11 and Debian 12 using test packages and ensure passing tests.
See [Main Release](https://johnduarte.gitlab.io/artemis_sg/release.html#main-release) for details.
* [ ] Update `CHANGELOG.md`.
  * Move "Unreleased" section to pending to "version" section e.g. "0.6.1".
  * Create clean "Unreleased" section.
  * Add "version" compare link e.g. "0.6.1".
  * Update "unreleased" compare link.
* [ ] Create tag for release e.g.:
```bash
git tag --sign v0.6.1
# Title to match tag; Body should be bullet list from `CHANGELOG.md`.
git push origin v0.6.1
```
* [ ] Create packages e.g.:
```bash
git checkout v0.6.1
hatch build -c
hatch publish -r test -u __token__ -a pypi-<SECRET_TOKEN>
hatch publish -u __token__ -a pypi-<SECRET_TOKEN>
```
* [ ] [Create release on gitlab](https://gitlab.com/johnduarte/artemis_sg/-/releases/new)
