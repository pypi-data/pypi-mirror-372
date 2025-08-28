export const description = 'CLI'

export const meta = {
  author: 'AJ Apte',
}

# Snapser CLI

Snapser has developed a CLI tool called **snapctl** that can be used on MaxOSX, Linux and Windows machines.
Snapctl will be the best way for game studios to integrate Snapser into their build pipelines.

## What's new in the latest version?
### Breaking Changes
1. Renamed SDK type `server` to `api-key` to be consistent with the Snapser Web app.

### Features
1. Added support for Bring your own Workstation commands. This enables local debugging for your BYOSnaps while clients continue to access your cloud Snapend APIs.
```bash
snapctl byows attach --snapend-id $snapend_id --byosnap-id $byosnap_id --http-port $http_port
```
```bash
snapctl byows reset --snapend-id $snapend_id
```

## Requirements
### Python 3.X and Pip
The Snapser CLI tool depends on Python 3.X and Pip. MacOS comes pre installed with Python. But
please make sure you are running Python 3.X. On Windows, you can download Python 3.X from the
Windows store.

### Docker
Some of the commands also need docker. You can download the latest version of Docker from the
[Docker website](https://www.docker.com/products/docker-desktop).

**IMPORTANT**: Open up Docker desktop and settings. Make sure this setting is disabled
**Use containerd for pulling and storing images**. This is because Snapser uses Docker
to build and push images to the Snapser registry. Having this setting enabled will
cause issues with the Snapser CLI tool.

## Installation

### Pip
Installing PIP on MacOS

```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

Installing PIP on Windows

```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

### Pipx
Now a days, pipx is recommended for CLI tools. Once you have Python and Pip installed, lets install `Pipx`.
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

### Install Snapctl
 - If you chose to use Pip
```bash
pip install --user snapctl
```

If you also have Python 2.X on your machine, you may have to run the following command instead

```bash
pip3 install --user snapctl
```
- If using, Pipx
```bash
pipx install snapctl
```

**IMPORTANT**: After you install snapctl you may have to add the python bin folder to your
path. For example, on MacOSX this is usually **~/Library/Python/3.9/bin**. On
Windows this is usually **C:\Users\username\AppData\Roaming\Python\Python39\Scripts**.
For, Windows users, after running pipx ensurepath, you may need to restart your terminal (Command Prompt, PowerShell, or Windows Terminal) for the PATH changes to take effect.


## Upgrade

Upgrade your snapctl version

- If using Pip

```bash
pip3 install --user snapctl --upgrade
```

- If using Pipx
```bash
pipx upgrade snapctl
```

## Setup

### Get your Snapser Access Key

Log in to your Snapser account. Click on your user icon on the top right and select, User Account.
In the left navigation click on **Developer** which will bring up your Personal API Key widget.
If you have not generated an API Key yet click on the **Generate** button to generate a new key.
You can generate up to 3 API Keys per user account.

**IMPORTANT**: Please make sure you save your API key in a safe place. You will not be able
to see it again.

### Setup a local config

You have three ways to pass the API key to Snapctl
1. Pass it via a command line argument with every command
2. Pass it via an environment variable
3. Pass it via a config file (recommended)

#### Command line argument

Every Snapser command can take a command line argument `--api-key <your_key>`. This will take precedence over
other methods.

#### Environment Variable

You can set an Environment variable `SNAPSER_API_KEY=<your_key>` and then run your snapctl commands. This will
be evaluated after verifying if there is any command line argument.

#### Config file

Create a file named `~/.snapser/config`. Open it using the editor of your choice and replace with your
personal Snapser Access key. Save the file. Advantage of using this method is you can use the `--profile`
argument with your snapctl command to use different API keys. NOTE: You may want to pass your own path
instead on relying on the default one the CLI looks for. You can do so by setting an environment
variable `SNAPSER_CONFIG_PATH='<your_custom_path>'`. Doing this will make sure that the CLI tool
will look for the config file at that path.

```
[default]
SNAPSER_API_KEY=$your_api_key
```

Or you can run the following command

on MacOSX

```
# $your_api_key = Your Snapser developer key
echo -e "[default]\nSNAPSER_API_KEY=$your_api_key" > ~/.snapser/config
```

on Windows Powershell

```
# $your_api_key = Your Snapser developer key
echo "[default]
SNAPSER_API_KEY=$your_api_key" | Out-File -encoding utf8 ~\.snapser\config
```

## Verify Snapctl installation

```
snapctl validate
```

Output will tell you if the Snapctl was able successfully validate your setup with the remote Snapser server
or not.

## Advanced Setup

Snapser by default supports access to multiple accounts. You can create multiple profiles in your Snapser config
**~/.snapser/config**.

```
[profile personal]
nSNAPSER_API_KEY=<key>

[profile professional]
nSNAPSER_API_KEY=<key>

```

You can then set an environment variable telling Snapser which profile you want to use.

```
# Mac
export SNAPSER_PROFILE="my_profile_name";

```

```
# Windows
setx SNAPSER_PROFILE="my_profile_name";

```

Or you can pass **--profile professional** with every command to tell Snapser to use a particular profile.

## Command variable name nomenclature
All commands follow these rules with their input variables
1. A variable that is named `*path` = CLI tool expects a path to a **folder**
2. A variable that is named `*filename` = CLI tool expects the name of the file, without the path.
3. A variable that is named `*path_filename` = CLI tool expects the full path. The folder up to the name of the file.

## Commands

Run the following to see the list of commands Snapser supports

```bash
snapctl --help
```

### BYO Snap - Bring your own Snap
Snapctl commands for your custom code

#### 1. byosnap help

See all the supported commands.

```bash
# Help for the byosnap command
snapctl byosnap --help
```

#### 2. byosnap generate-profile

This command generates a base BYOSnap profile. You will have to update the values within this file
and then you can use it in commands like `publish` and `sync`. It is recommended that you save this
file at the root of your BYOSnap code and commit it to version control.

```bash
# Help for the byosnap command
snapctl byosnap generate-profile --help

# Generate your BYOSnap profile
# $output_path = Directory where you want the BYOSnap profile to be saved.
# $profile_filename = Name of the BYOSnap profile you want to give. Only .json, .yaml, .yml extensions
#   are allowed. If you do not pass `--profile-filename` then Snapser choses
#   `snapser-byosnap-profile.json` as the filename.
snapctl byosnap generate-profile --out-path $output_path --profile-filename $profile_filename
snapctl byosnap generate-profile --out-path /Users/DevName/Development/SnapserEngine/byosnap-python --profile-filename=my-byosnap-profile.json
snapctl byosnap generate-profile --out-path /Users/DevName/Development/SnapserEngine/byosnap-python --profile-filename=my-byosnap-profile.yaml
```

#### 3. byosnap validate-profile

This command validates your BYOSnap profile.

```bash
# Help for the byosnap command
snapctl byosnap validate-profile --help

# Validate your BYOSnap profile
# $path = Directory Path to where your BYOSnap Profile is located. No need to add the file name.
# $resources_path = Optionally, you can place your BYOSnap profile at your resources path
# $profile_filename = Optional parameter. Name of your BYOSnap profile.
#   If you do not pass `--profile-filename` then
#   Snapser choses the default `snapser-byosnap-profile.json` as the filename to validate
snapctl byosnap validate-profile --path $path
snapctl byosnap validate-profile --resources-path $resources_path --profile-filename $profile_filename
snapctl byosnap validate-profile --path /Users/DevName/Development/SnapserEngine/byosnap-python
snapctl byosnap validate-profile --path /Users/DevName/Development/SnapserEngine/byosnap-python --profile-filename my-byosnap-profile.yaml
```

#### 4. byosnap publish

This command allows you to create and publish your BYOSnap. Running this command will first create a BYOSnap namespace on Snapser if not present. Then it will build and publish your code to your own
private ECR repo on Snapser. Finally it will assign a version to your BYOSnap so that you
can deploy it.

**Requirements**:
- This command needs docker.
- This command needs a BYOSnap profile. BYOSnap profile, holds information about
your BYOSnap like, name, description, etc and hardware requirements like CPU, Memory. We
recommend you store this file at the root of your BYOSnap and also add it to version control.
You can generate it using `snapctl byosnap generate-profile --out-path $outputPath --profile-filename $profileName`.

```bash
# Help for the byosnap command
snapctl byosnap publish --help

# Create and publish your BYOSnap
# $byosnap_id = Snap ID for your snap
# $version = Semantic version for your snap Eg: v0.0.1
# $code_root_path = Local code path where your Dockerfile is present
# $resources_path = Optional path to the resources directory in your Snap. This ensures, you are not forced to put the Dockerfile, snapser-byosnap-profile.json, swagger.json and README.md at the root directory of your Snap.
# $profile_filename = Optional parameter. Name of your BYOSnap profile.
#   If you do not pass `--profile-filename` then
#   Snapser choses the default `snapser-byosnap-profile.json` as the filename to validate
# $skip-build = true/false. Default is false. Pass this flag as true to skip the build and head straight to tag and push. Build step needs to run and tag using the --tag you pass to the publish-image command for this to work. Make sure the tag matches the version number you are passing.
# Example:
snapctl byosnap publish --byosnap-id byosnap-jinks-flask --version "v0.0.1" --path /Users/DevName/Development/SnapserEngine/byosnap-python --profile-filename $profile_filename
snapctl byosnap publish --byosnap-id $byosnap_id --version $version --path $code_root_path
byosnap publish --byosnap-id byosnap-python --version "v1.0.0" --path /Users/AJ/Development/byosnap-python --profile-filename my-byosnap-profile.yaml
```

#### 5. byosnap sync

This command is for development purposes. It allows developers to rapidly build, update and push their BYOSnap to a dev Snapend. Simply, make changes to your code locally, and then run this command to deploy your BYOSnap straight to your development Snapend.

**Requirements**:
- This command needs docker.

**IMPORTANT**: This command will only work for Dev Snapends. Additionally if the version you are using in this command happens to be used by a staging or a production snapend then `sync` will not work. We do this to ensure that your staging and production BYOSnap images do not get impacted.

```bash
# Help for the byosnap command
snapctl byosnap sync --help

# Deploy local code straight to your Snapend
# $byosnap_id = Snap ID for your snap
# $code_root_path = Local code path where your Dockerfile is present
# $resources_path = Optional path to the resources directory in your Snap. This ensures, you are not forced to put the Dockerfile, swagger.json and README.md in the root directory of your Snap.
# $skip-build = true/false. Default is false. Pass this flag as true to skip the build and head straight to tag and push. Build step needs to run and tagged using the --tag you pass to the publish-image command for this to work.
# $tag = Semantic version for your snap Eg: v0.0.1
# $version =
# $snapend_id = Dev Snapend Id
# Example:
snapctl byosnap sync --byosnap-id byosnap-jinks-flask --path /Users/DevName/Development/SnapserEngine/byosnap-python --version "v0.0.11" --snapend-id "jxmmfryo"
snapctl byosnap sync --byosnap-id $byosnap_id --path $code_root_path --version $version --snapend-id $snapend_id
```

#### 6. byosnap create

Create a custom snap. Note that you will have to build, push and publish your snap image, for it to be useable
in a Snapend.

```bash
# Help for the byosnap command
snapctl byosnap create --help

# Create a new snap
# $byosnap_id = Snap ID for your snap. Start start with `byosnap-`
# $name = User friendly name for your BYOSnap
# $desc = User friendly description
# $platform = One of linux/arm64, linux/amd64
# $language = One of go, python, ruby, c#, c++, rust, java, node

# Example:
# snapctl byosnap create --byosnap-id byosnap-jinks-flask --name "Jinks Flask Microservice" --desc "Custom Microservice" --platform "linux/arm64" --language "go"
snapctl byosnap create --byosnap-id $byosnap_id --name "$name" --desc "$desc" --platform "$platform" --language "$language"
```

#### 7. byosnap build

Build your snap image

```bash
# Help for the byosnap command
snapctl byosnap build --help

# Publish a new image
# $byosnap_id = Snap ID for your snap
# $image_tag = An image tag for your snap
# $code_root_path = Local code path where your Dockerfile is present
# $resources_path = Optional path to the resources directory in your Snap. This ensures, you are not forced to put the Dockerfile, swagger.json and README.md in the root directory of your Snap.
# Example:
# snapctl byosnap build --byosnap-id byosnap-jinks-flask --tag my-first-image --path /Users/DevName/Development/SnapserEngine/byosnap-python
snapctl byosnap build --byosnap-id $byosnap_id --tag $image_tag --path $code_root_path
snapctl byosnap build --byosnap-id $byosnap_id --tag $image_tag --path $code_root_path --resources-path $resources_path
```

#### 8. byosnap push

Push your snap image to Snapser

```bash
# Help for the byosnap command
snapctl byosnap push --help

# Publish a new image
# $byosnap_id = Snap ID for your snap
# $image_tag = An image tag for your snap
# Example:
# snapctl byosnap push --byosnap-id byosnap-jinks-flask --tag my-first-image
snapctl byosnap push --byosnap-id $byosnap_id --tag $image_tag
```

#### 9. byosnap upload-docs

Upload swagger.json and README.md for you Snap

```bash
# Help for the byosnap command
snapctl byosnap upload-docs --help

# Publish a new image
# $byosnap_id = Snap ID for your snap
# $image_tag = An image tag for your snap
# $resources_path = Path to your swagger.json and README.md files
# Example:
# snapctl byosnap upload-docs --byosnap-id byosnap-jinks-flask --tag my-first-image --resources-path /Users/DevName/Development/SnapserEngine/byosnap-python
snapctl byosnap upload-docs --byosnap-id $byosnap_id --tag $image_tag --resources-path $resources_path
```

#### 10. byosnap publish-image

Publish a custom snap code image. This command executes, `build`, `push` and `upload-docs` one
after the other.

**IMPORTANT**: Take note of the hardware architecture of machine and your Dockerfile commands.
Commands in docker file may be hardware architecture specific. Snapser throws a warning if it detects
a mismatch.

```bash
# Help for the byosnap command
snapctl byosnap publish-image --help

# Publish a new image
# $byosnap_id = Snap ID for your snap
# $image_tag = An image tag for your snap
# $code_root_path = Local code path where your Dockerfile is present
# $resources_path = Optional path to the resources directory in your Snap. This ensures, you are not forced to put the Dockerfile, swagger.json and README.md in the root directory of your Snap.
# $skip-build = true/false. Default is false. Pass this flag as true to skip the build and head straight to tag and push. Build step needs to run and tagged using the --tag you pass to the publish-image command for this to work.
# Example:
# snapctl byosnap publish-image --byosnap-id byosnap-jinks-flask --tag my-first-image --path /Users/DevName/Development/SnapserEngine/byosnap-python
snapctl byosnap publish-image --byosnap-id $byosnap_id --tag $image_tag --path $code_root_path
snapctl byosnap publish-image --byosnap-id $byosnap_id --tag $image_tag --path $code_root_path --resources-path $resources_path
snapctl byosnap publish-image --byosnap-id $byosnap_id --tag $image_tag --skip-build
```

#### 11. byosnap publish-version

Publish a new version for your Snap. Only after your Snap version is published, you will be able
to use your snap in your Snapend. This command should be run after `push` or `publish-image` commands.

IMPORTANT: You need to have $byosnapProfile to run this command. BYOSnap profile is a JSON configuration
of your BYOSnap for the development, staging and production environments. You can generate a base version of this file using the `snapctl byosnap generate-profile --out-path $outputPath --profile-filename $profileName` command.

```bash
# Help for the byosnap command
snapctl byosnap publish-version --help

# Publish a new image
# $byosnap_id = Snap ID for your snap
# $image_tag = An image tag for your snap
# $version = Semantic version for your snap Eg: v0.0.1
# $byosnap_profile_path = Path to the snapser-byosnap-profile.json BYOSnap profile to configure dev, stage and prod settings for this snap. You can generate a base version of this file using the `snapctl byosnap generate-profile --out-path $outputPath --profile-filename $profileName` command
# Example:
# snapctl byosnap publish-version --byosnap-id byosnap-jinks-flask --tag my-first-image --version v0.0.1 --path /Users/DevName/Development/SnapserEngine/byosnap-python
snapctl byosnap publish-version --byosnap-id $byosnap_id --tag $image_tag --version $version --path $byosnap_profile_path
```

### BYO Workstation - Bring your own Workstation
Snapctl commands for bring your own workstation. This command allows you to attach your workstation to a Snapend. This is useful for testing and debugging your BYOSnap code.

#### 1. byows help
See all the supported commands

```bash
# Help for the byows command
snapctl byows --help
```
#### 2. byows attach
Attach your workstation to a Snapend. It should be noted, that this command outputs a file `byows_env_setup.sh|ps1` at `~/.snapser/` directory. This file contains the environment variables that the BYOWS technology will need to route internal calls to the appropriate Snaps.

```bash
# Attach your workstation to a Snapend
# $snapend_id = Snapend Id
# $byosnap_id = BYOSnap Id
# $http_port = Port that your local server is running on
snapctl byows attach --snapend-id $snapend_id --byosnap-id $byosnap_id --http-port $http_port
```

Then run, the following command in a separate terminal window, to setup the BYOWS environment variables.
```bash
# MacOSX
source ~/.snapser/byows_env_setup.sh
# Windows
.\.snapser\byows_env_setup.ps1
```

Then start your BYOSnap local server in the same tab that has the environment variables set up. This will ensure that the BYOSnap code can access the internal SDK and other Snaps in your Snapend.

### BYO Game Server - Bring your own Game Server
Snapctl commands for your custom game server

#### 1. byogs help

See all the supported commands

```bash
# Help for the byogs command
snapctl byogs --help
```

#### 2. byogs publish

Publish your custom game server image. This commend replaces the old way of creating, publishing image and
then publishing the byogs. Now all you have to do is publish your image and create a fleet using the web portal.

**IMPORTANT**: Take note of the hardware architecture of machine and your Dockerfile commands.
Commands in docker file may be hardware architecture specific. Snapser throws a warning if it detects
a mismatch.

```bash
# Help for the byogs command
snapctl byogs publish --help

# Publish a new image
# $image_tag = An image tag for your snap
# $code_root_path = Local code path where your Dockerfile is present
# $resources_path = Optional path to the resources directory. This ensures, you are not forced to put the Dockerfile at the root directory of your Game Server code.
# $skip-build = Default is false. Pass this flag as true to skip the build and head straight to tag and push. Build step needs to run and tagged using the --tag you pass to the publish-image command for this to work.
# Example:
# snapctl byogs publish --tag my-first-image --path /Users/DevName/Development/SnapserEngine/game_server
snapctl byogs publish --tag $image_tag --path $code_root_path
snapctl byogs publish --tag $image_tag --path $code_root_path --resources-path $resources_path
snapctl byogs publish --tag $image_tag --skip-build
```

#### 3. byogs sync

This command allows developers to rapidly build, update and push their BYOGs out to a Snapend fleet. Simply, make changes to your code locally, and then run this command to deploy your BYOGs straight to your Snapend fleet.

```bash
# Help for the byogs command
snapctl byogs sync --help

# Publish a new image
# $code_root_path = Local code path where your Dockerfile is present
# $resources_path = Optional path to the resources directory in your Snap. This ensures, you are not forced to put the Dockerfile, swagger.json and README.md in the root directory of your Snap.
# $skip-build = true/false. Default is false. Pass this flag as true to skip the build and head straight to tag and push. Build step needs to run and tagged using the --tag you pass to the publish-image command for this to work.
# $image_tag = An image tag for your snap. Note snapctl adds a timestamp, allowing you to use the same command.
# $snapend_id = Snapend Id
# $fleet_names = Comma separated fleet names
# Example:
snapctl byogs sync --path /Users/DevName/Development/SnapserEngine/game_server --tag my-first-image --snapend-id "jxmmfryo" --fleet-names "my-fleet,my-second-fleet"
snapctl byosnap sync --path $code_root_path --tag $image_tag --snapend-id $snapend_id --fleet-names $fleet_names
```

#### 4. byogs build

Build your custom game server image.

```bash
# Help for the byogs command
snapctl byogs build --help

# Publish a new image
# $image_tag = An image tag for your snap
# $code_root_path = Local code path where your Dockerfile is present
# Example:
# snapctl byogs build byosnap-jinks-gs --tag my-first-image --path /Users/DevName/Development/SnapserEngine/game_server
snapctl byogs build --tag $image_tag --path $code_root_path
```

#### 5. byogs push

Push your custom game server image.

```bash
# Help for the byogs command
snapctl byogs push --help

# Publish a new image
# $image_tag = An image tag for your snap
# Example:
# snapctl byogs push byosnap-jinks-gs --tag my-first-image
snapctl byogs push --tag $image_tag
```


### Game
Snapctl commands for your game

#### 1. game help

See all the supported commands

```bash
# Help for the byogs command
snapctl game --help
```

#### 2. game create
Create a game
```bash
snapctl game create --name $game_name
```

#### 3. game enumerate
List all the games
```bash
snapctl game enumerate
```

### Snapend
Snapctl commands for your snapend

#### 1. snapend help

See all the supported commands

```bash
# Help for the snapend command
snapctl snapend --help
```

#### 2. snapend download

Download Manifest, SDKs and Protos for your Snapend

```bash
# Help for the download command
snapctl snapend download --help

# Download your Snapend SDK and Protos
# $snapend_id = Cluster Id
# $category = snapend-manifest, sdk, protos
# $format = One of the supported formats:
#   snapend-manifest(yaml, json)
#   sdk(unity, unreal, roblox, godot, cocos, ios-objc, ios-swift, android-java, android-kotlin, web-ts, web-js),
#   sdk(csharp, cpp, lua, ts, go, python, kotlin, java, c, node, js, perl, php, closure, ruby, rust),
#   protos(go, csharp, cpp, raw)
# $type = One of the supported types:
#   For category=sdk type=(user, server, internal, app)
#   For category=protos type=(messages, services)
# $http_lib (optional) = One of the supported libs
#   For category=sdk format=unity http-lib=(httpclient, unitywebrequest, restsharp)
#   For category=sdk format=csharp http-lib=(httpclient, restsharp)
#   For category=sdk format=web-ts http-lib=(axios, fetch)
#   For category=sdk format=ts http-lib=(axios, fetch)
# Example:
# snapctl snapend download --snapend-id gx5x6bc0 --category snapend-manifest --format yaml --out-path .
# snapctl snapend download --snapend-id gx5x6bc0 --category sdk --format unity --type user --out-path .
# snapctl snapend download --snapend-id gx5x6bc0 --category sdk --format cpp --type internal --out-path .
# snapctl snapend download --snapend-id gx5x6bc0 --category protos --format raw --type messages --out-path .
# snapctl snapend download --snapend-id gx5x6bc0 --category sdk --format unity --type user --http-lib unitywebrequest --out-path .
snapctl snapend download --snapend-id $snapend_id --category $category --format $format --type $type --out-path $out_path
snapctl snapend download --snapend-id $snapend_id --category $category --format $format --type $type --http-lib $http_lib --out-path $out_path
```

#### 3. snapend clone

Clone a Snapend from an existing manifest. Passing the blocking flag ensures your CLI command waits till the new Snapend is up.

```bash
# Help for the clone command
snapctl snapend clone --help

# Clone your Snapend
# $game_id = Game Id
# $snapend_name = Name of your new Snapend
# $env = One of development, staging
# $path_to_manifest = Path to the manifest file; should include the file name
# Example:
# snapctl snapend clone --game-id 2581d802-aca-496c-8a76-1953ad0db165 --name new-snapend --env development --manifest-path-filename "C:\Users\name\Downloads\snapser-ox1bcyim-manifest.json" --blocking
snapctl snapend clone --game-id $game_id --name $snapend_name --env $env --manifest-path-filename "$path_to_manifest"
snapctl snapend clone --game-id $game_id --name $snapend_name --env $env --manifest-path-filename "$path_to_manifest" --blocking
```

#### 4. snapend apply

Apply changes to your Snapend from a manifest. You should have the latest manifest before applying changes. Basically, when you download a manifest, Snapser adds an `applied_configuration` section to your manifest, which stores the state of the Snapend during export. Now, if someone manually updates the Snapend or a configuration of a Snap, you are no longer going to have the latest Snapend representation in the `applied_configuration`. This is how Snapser prevents you from stomping over someone elses changes.

You can optionally pass a `--force` flag telling Snapser to ignore any diffs it may find in the current state of the Snapend and the one in the `applied_configuration` field of your manifest. Essentially, this flag allows you to stomp over any changes and tell Snapser to force apply.

Separately, you can pass a blocking flag to make your CLI wait for the Snapend update to complete.


```bash
# Help for the apply command
snapctl snapend apply --help

# Apply changes to a snapend via manifest
# $path_to_manifest = Path to the manifest file; should include the file name
# --force = Optional flag to tell Snapser that you do not want it to check the diff between the Snapend states and just force apply the changes
# Example:
# snapctl snapend apply --manifest-path-filename "C:\Users\name\Downloads\snapser-ox1bcyim-manifest.json" --force --blocking
snapctl snapend apply --manifest-path-filename "$path_to_manifest"
snapctl snapend apply --manifest-path-filename "$path_to_manifest" --blocking
snapctl snapend apply --manifest-path-filename "$path_to_manifest" --force --blocking
```

#### 5. snapend update

Update your BYOSnap or BYOGs versions for the Snapend

```bash
# Help for the byogs command
snapctl snapend update --help

# Update your Snapend with new BYOSnaps and BYOGs
# $snapend_id = Cluster Id
# $byosnaps = Comma separated list of BYOSnap ids and version.
# $byogs = Comma separated list of BYOGs fleet name, id and version.
# --blocking = (Optional) This makes sure the CLI waits till your Snapend is live.
# Note at least one of the two needs to be present
# Example:
# snapctl snapend update --snapend-id gx5x6bc0 --byosnaps byosnap-service-1:v1.0.0,byosnap-service--2:v1.0.0 --byogs byogs-fleet-one:gs-1:v0.0.1,my-fleet-two:gs-2:v0.0.4
# snapctl snapend update --snapend-id gx5x6bc0 --byosnaps byosnap-service-1:v1.0.0,byosnap-service--2:v1.0.0 --byogs fleet-one:v0.0.1,fleet-two:v0.0.4 --blocking
snapctl snapend update --snapend-id $snapend_id --byosnaps $byosnaps --byogs $byogs --blocking
```

#### 6. snapend state

Get the Snapend state

```bash
# Help for the byogs command
snapctl snapend state --help

# Get the Snapend state
# $snapend_id = Cluster Id
# Example:
# snapctl snapend state gx5x6bc0
snapctl snapend state $snapend_id
```

### Generate
Generator tool to help generate credentials

#### 1. generate help
See all the supported commands
```bash
# Help for the generate command
snapctl generate --help
```

#### 2. Generate ECR Credentials
Generate the ECR credentials. Game studios can use these credentials to self publish their images to Snapser.

```bash
snapctl generate credentials --category "ecr" --out-path $output_path

```


## Error codes
### CLI Return Codes
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 0          | Operation completed successfully                         |
| 1          | General error                                            |
| 2          | Input error                                              |
| 3          | Resource not found                                       |

### Configuration Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 10         | Configuration incorrect                                  |
| 11         | Configuration error                                      |
| 12         | Dependency missing                                       |

### BYOGS Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 3          | BYOGs resource not found                                 |
| 20         | Generic BYOGS error                                      |
| 21         | BYOGS dependency missing                                 |
| 22         | BYOGS ECR login error                                    |
| 23         | BYOGS build error                                        |
| 24         | BYOGS tag error                                          |
| 25         | BYOGS publish error                                      |
| 26         | BYOGS publish permission error                           |
| 27         | BYOGS publish duplicate tag error                        |

### BYOSNAP Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 3          | BYOSnap resource not found                               |
| 30         | Generic BYOSNAP error                                    |
| 31         | BYOSNAP dependency missing                               |
| 32         | BYOSNAP ECR login error                                  |
| 33         | BYOSNAP build error                                      |
| 34         | BYOSNAP tag error                                        |
| 35         | BYOSNAP publish image error                              |
| 36         | BYOSNAP publish image permission error                   |
| 37         | BYOSNAP publish image duplicate tag error                |
| 38         | BYOSNAP create error                                     |
| 39         | BYOSNAP create permission error                          |
| 40         | BYOSNAP create duplicate name error                      |
| 41         | BYOSNAP publish version error                            |
| 42         | BYOSNAP publish version permission error                 |
| 43         | BYOSNAP publish version duplicate version error          |
| 44         | BYOSNAP publish version duplicate tag error              |
| 45         | BYOSNAP update version error                             |
| 46         | BYOSNAP update version service in use                    |
| 47         | BYOSNAP update version tag error                         |
| 48         | BYOSNAP update version invalid version error             |
| 49         | BYOSNAP publish error                                    |
| 86         | BYOSNAP generate-profile                                 |
| 87         | BYOSNAP swagger error                                    |


### Game Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 3          | Game resource not found                                  |
| 50         | Generic game error                                       |
| 51         | Game create error                                        |
| 52         | Game create permission error                             |
| 53         | Game create limit error                                  |
| 54         | Game create duplicate name error                         |
| 55         | Game enumerate error                                     |

### Snapend Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 3          | Snapend resource not found                               |
| 60         | Generic snapend error                                    |
| 61         | Snapend enumerate error                                  |
| 62         | Snapend clone error                                      |
| 63         | Snapend clone server error                               |
| 64         | Snapend clone timeout error                              |
| 65         | Snapend apply error                                      |
| 66         | Snapend apply server error                               |
| 67         | Snapend apply timeout error                              |
| 68         | Snapend promote error                                    |
| 69         | Snapend promote server error                             |
| 70         | Snapend promote timeout error                            |
| 71         | Snapend download error                                   |
| 72         | Snapend update error                                     |
| 73         | Snapend update server error                              |
| 74         | Snapend update timeout error                             |
| 75         | Snapend state error                                      |
| 76         | Snapend manifest mismatch error                          |

### Generate Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 80         | Generic generate error                                   |
| 81         | Generate credentials error                               |

### BYOWS Errors
| Error Code | Description                                              |
|------------|----------------------------------------------------------|
| 95         | Generic byows error                                      |
| 96         | Byows attach error                                       |
| 97         | Byows reset error                                        |
