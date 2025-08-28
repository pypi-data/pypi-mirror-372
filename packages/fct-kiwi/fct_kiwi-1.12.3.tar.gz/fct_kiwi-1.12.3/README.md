# FCT-Kiwi

A command-line tool for Balena device configuration management, allowing you to easily change, clone, purge, retrieve, and manage variables across devices and fleets.

## Table of Contents

- [FCT-Kiwi](#fct-kiwi)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Authentication](#authentication)
    - [Environment variables](#environment-variables)
    - [Schedule Permissions](#schedule-permissions)
    - [Google Sheets Logging](#google-sheets-logging)
  - [Commands](#commands)
    - [Usage in other scripts](#usage-in-other-scripts)
    - [Change](#change)
    - [Clone](#clone)
    - [Purge](#purge)
    - [Get](#get)
    - [Delete](#delete)
    - [Move](#move)
    - [Schedule](#schedule)
      - [Schedule change](#schedule-change)
      - [Schedule update](#schedule-update)
    - [Initialize](#initialize)
    - [Rename](#rename)
    - [Converter](#converter)
    - [Pin](#pin)
  - [File Format](#file-format)
    - [Changing variables](#changing-variables)
    - [Scheduling](#scheduling)
      - [Variable changes](#variable-changes)
      - [Pin devices to release](#pin-devices-to-release)
    - [Tags by version](#tags-by-version)
  - [Error Handling](#error-handling)
  - [Dependencies](#dependencies)
  - [Author](#author)

## Installation

```bash
pip install fct-kiwi
```

## Authentication

To use this tool, you need to set up some environment variables if you haven't already, please refer to the [Environment variables](#environment-variables) section to set all the variables that don't have a default, this can be done in your terminal as environment variables, for example:

`export BALENA_API_KEY="your_api_key_here"`

Or an environment variables file to handle all at once can be defined as shown in the next section.



### Environment variables

By default, this is the order in which variables are read:

1. `.env` file
2. default
3. os.environ

Other variables might be needed for certain commands and are set by default, but can be overridden if necessary.

1. Create a `.env` file in the same directory as the script or set the path into your environment as `export FCT_ENV_PATH="/path/to/my/.env"`
2. Add your Balena API key: `BALENA_API_KEY=your_api_key_here`
3. Add other variables as needed.

**Note:**

✔ in the Required column means the variable is required for the script to function.

Empty Default fields mean the variable is optional unless needed by a specific command.

| Variable                        | Description                    | Default                 | Required |
| ----------------------          | ----------------------------   | ----------------------- | -------- |
|`BALENA_API_KEY`                 | Balena API key                 |                         | ✔        |
|`PROJECT_ID`                     | GCP Project                    |                         |          |
|`SPREADSHEET_NAME`               | Google Sheets file for logging | SD Logs                 |          |
|`LOCATION_ID`                    | GCP Queue location             |                         |          |
|`QUEUE_ID`                       | GCP Queue identifier           |                         |          |
|`GOOGLE_APPLICATION_CREDENTIALS` | GCP Service account file       |                         |          |
|`TAGS_BY_VERSION_FILE`           | Tags by version file location  | tags_by_version.json    |          |

### Schedule Permissions

To use the schedule commands, you need to set up Google Cloud Platform (GCP) with the following permissions and resources:

#### Required GCP Permissions

Your account (or service account) needs the following IAM roles:

- **Cloud Tasks Enqueuer** (`roles/cloudtasks.enqueuer`) - To create and manage Cloud Tasks
- **Service Account User** (`roles/iam.serviceAccountUser`) - To execute tasks with the service account

#### Required GCP Resources

1. **Project**: A GCP project where the resources are created
2. **Cloud Tasks Queue**: A queue to handle the scheduled tasks
3. **Service Account**: A service account with the required permissions to send http requests to the pub/sub topic

#### Setup Steps GCP

1. Create a GCP project or use an existing one
2. Enable the Cloud Tasks API: `gcloud services enable cloudtasks.googleapis.com`
3. Create a service account with the required permissions
4. Create a Cloud Tasks queue in your desired location
5. Set the service account usage permissions
   - Give your user permissions to act as the service account: `gcloud iam service-accounts add-iam-policy-binding SERVICE_ACCOUNT_EMAIL --member="user:YOUR_EMAIL" --role="roles/iam.serviceAccountUser"`
      - Login using [gcloud-cli](https://cloud.google.com/sdk/docs/install) on your machine
   - OR Download the service account key: `gcloud iam service-accounts keys create key.json --iam-account=SERVICE_ACCOUNT_EMAIL` (give it the appropriate permissions)
      - And set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable: `export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"`

> [!IMPORTANT]
> If you will use the ADC crendentials for your account you need to login with the correct scopes with the following command:
```
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/sqlservice.login,https://www.googleapis.com/auth/userinfo.email,openid,"https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"
```

### Google Sheets Logging

The tool includes logging functionality that writes operations to Google Sheets for audit and tracking purposes.

#### Required Permissions

Your gcp user or service account needs the following permissions for Google Sheets:

- **Google Sheets API access** - To read and write to spreadsheets
- **Drive API access** - To access and modify spreadsheet files

#### Setup Steps

1. Enable the Google Sheets API in your GCP project: `gcloud services enable sheets.googleapis.com`
2. Enable the Google Drive API: `gcloud services enable drive.googleapis.com`
3. Create a Google Sheets file and share it with your google email or service account email
4. Set the `SPREADSHEET_NAME` environment variable to the name of your spreadsheet

#### Logged Information

The following operations are logged to Google Sheets:

- Device moves and renames
- Scheduled operations

## Commands

### Help

To get help on how to use the package, you can use the following command:

```bash
fct --help
```

Also, you can use the following command to get help on a specific command:

```bash
fct <command> --help
```

### Usage in other scripts

To use this packages functionality in other scripts simply import the functions you need from the following list.

```python
from fleet_control import clone, change, etc...
```

Otherwise you can use all commands from your terminal.

### Change

Change or create specified variable(s) to target device(s).

```bash
# Basic usage
fct change 'VAR_NAME=0=*' 4X002 4X003

# Change multiple variables
fct change 'VAR_NAME=0=* ANOTHER_VAR=value=service_name' 4X002 4X003

# Target a fleet
fct change 'VAR_NAME=0=*' FLEET_NAME

# Use a file containing variables
fct change --file variables.txt '' 4X002 4X003
```

### Clone

Clone configuration from a source device or fleet to target device(s).

```bash
# Clone from one device to others
fct clone 4X001 4X002 4X003

# Clone from a fleet to a device
fct clone FLEET_NAME 4X002

# Clone from a fleet to another fleet
fct clone FLEET_NAME ANOTHER_FLEET_NAME

# Clone with exclusions
fct clone --exclude "VAR1 VAR2" 4X001 4X002 4X003
```

### Purge

Purge all custom variables in target device(s).

```bash
# Purge all custom variables from devices
fct purge 4X001 4X002 4X003

# Purge with exclusions
fct purge --exclude "VAR1 VAR2" 4X001 4X002 4X003
```

### Get

Fetch variable value(s) for a device.

```bash
# Get a specific variable
fct get VAR_NAME 4X001 4X002 4X003

# Get all custom variables
fct get --custom '' 4X001 4X002 4X003

# Get all variables (device + fleet)
fct get --all-vars '' 4X001 4X002 4X003

# Save variables to a file
fct get --output result.json VAR_NAME 4X001

# Output in YAML format
fct get --output-yaml VAR_NAME 4X001 4X002 4X003
```

### Delete

Delete the overwritten value for specified variable(s) on the target device(s).

```bash
# Delete a variable
fct delete 'VAR_NAME=0=*' 4X002 4X003

# Delete multiple variables
fct delete 'VAR1=value=service VAR2=value=*' 4X002 4X003

# Delete variables from a file
fct delete --file variables.txt '' 4X002 4X003
```

### Move

Move target(s) from its current fleet to a specified fleet.

```bash
# Move devices to a new fleet
fct move FLEET_NAME 4X001 4X002 4X003

# Move keeping custom device variables
fct move --keep-vars FLEET_NAME 4X001 4X002 4X003

# Move keeping custom device and service variables
fct move --keep-service-vars FLEET_NAME 4X001 4X002 4X003

# Move with cloning (keep custom and previous fleet variables)
fct move --clone FLEET_NAME 4X001 4X002 4X003

# Move and pin to specific release
fct move --semver "1.3.11+rev87" FLEET_NAME 4X001 4X002 4X003
```

### Schedule

Schedule functions to run at a specific time. Service account file path required for creating the task. Set with the `GOOGLE_APPLICATION_CREDENTIALS` variable set in the `.env` file or in your environment.

**Required environment variables for all schedule commands:**

- `PROJECT_ID` (GCP Project)
- `LOCATION_ID` (GCP Queue location)
- `QUEUE_ID` (GCP Queue identifier)
- `SERVICE_ACCOUNT` (path to your Google service account credentials)

#### Schedule change

Change or create specified variable(s) to target device(s).

```bash
# Schedule a change for tomorrow at 3 AM (default)
fct schedule change 'VAR_NAME=0=main' 4X001 4X002

# Schedule with a specific date and time
fct schedule change --date '2025-02-25 12:06:00' 'VAR_NAME=0=main' 4X001 4X002

# Schedule with a file containing variables
fct schedule change --date '2025-02-25 12:06:00' --file vars.json 

# Schedule with different timezone
fct schedule change --tz 'America/New_York' 'VAR_NAME=0=main' 4X001 4X002
```

#### Schedule update

Pins the specified devices to the selected release in that fleet.

```bash
# Schedule a pin to release for tomorrow at 3 AM (default)
fct schedule update FLEET_NAME 1.3.19+rev43 4X001 4X002

# Direct input with date and timezone
fct schedule update --date '2025-04-01T15:30:00Z' --tz 'Europe/London' FLEET_NAME 1.3.19+rev43 4X001 

# Use a JSON file for targets and release info
fct schedule update --date '2025-02-25 12:06:00' --file file.json 
```

### Initialize

Initialize a target device with previous device tags, remove old device, delete default config variables, and move to specified fleet.

```bash
# Initialize a device and move it to a fleet
fct initialize FLEET_NAME 4X001
```

### Rename

Rename a target device with new ID. Optional new tags for corresponding version read from configuration file. Configuration file path set with the `TAGS_BY_VERSION_FILE` variable set in the `.env` file or in your environment.

**Required environment variables:**

- `SERVICE_ACCOUNT` (path to your Google service account credentials)
- `SPREADSHEET_NAME` (Google Sheets file for logging)

```bash
# Rename a device
fct rename 4A001 4B222

# Rename a device and specify new version
fct rename --version "4.3F" 4A001 4B222
```

### Converter

Convert a shell env var file to a JSON config file. All variables starting with `NODE_` go to `env_vars`. All others go to `service_vars > main`.

```bash
# Convert a shell env var file to JSON config
fct converter input.sh output.json
```

### Pin

Pin target device(s) to a specific fleet release. If no targets are specified, pins the entire fleet. You can also pin all devices in a fleet or exclude specific devices.

```bash
# Pin specific devices to a release
fct pin FLEET_NAME 4X001 4X002 4X003

# Pin a fleet to a specific release
fct pin FLEET_NAME --semver 1.3.12+rev12

# Pin all devices in a fleet
fct pin FLEET_NAME --all

# Pin all devices except some
fct pin FLEET_NAME --all --exclude 4X001 4X002
```

## File Format

### Changing variables

When using the `--file` option, the file should contain JSON formatted variables:

```json
{
  "env_vars": {
      "VAR1_NAME": "VAR1_VALUE",
      "VAR2_NAME": 2
  },
  "service_vars": {
      "main": {
        "SERVICE_VAR1_NAME": "SERVICE_VAR1_VALUE",
        "SERVICE_VAR2_NAME": "SERVICE_VAR2_VALUE"
      }
  }
}
```

### Scheduling

#### Variable changes

```json
{
  "targets": [
    "TARGET1_NAME",
    "TARGET2_NAME"
  ],
  "variables": {
    "env_vars": {
        "VAR1_NAME": "VAR1_VALUE",
        "VAR2_NAME": 2
    },
    "service_vars": {
        "main": {
          "SERVICE_VAR1_NAME": "SERVICE_VAR1_VALUE",
          "SERVICE_VAR2_NAME": "SERVICE_VAR2_VALUE"
        }
    }
  }
}
```

#### Pin devices to release

```json
{
    "targets": [
        "TARGET1_NAME",
        "TARGET2_NAME"
    ],
    "fleet": "FLEET_NAME",
    "release": "RELEASE_SEMVER"
}
```

### Tags by version

```json
{
    "4.3B":{
        "Tag1": "value1",
        "Tag2": "value2",
    }
}
```

## Error Handling

The tool will return appropriate error messages if:

- The Balena API key is not set
- No variables are provided when required
- Target devices or fleets cannot be found
- API requests fail

## Dependencies

- balena-sdk
- click
- python-dotenv

## Author

Juan Pablo Castillo - <juan.castillo@kiwibot.com>
