# AA Inactivity

This is a player activity monitoring plugin app for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth) (AA).

[![release](https://img.shields.io/pypi/v/aa-inactivity?label=release)](https://pypi.org/project/aa-inactivity/)
[![python](https://img.shields.io/pypi/pyversions/aa-inactivity)](https://pypi.org/project/aa-inactivity/)
[![django](https://img.shields.io/pypi/djversions/aa-inactivity?label=django)](https://pypi.org/project/aa-inactivity/)
[![pipeline](https://gitlab.com/eclipse-expeditions/aa-inactivity/badges/master/pipeline.svg)](https://gitlab.com/eclipse-expeditions/aa-inactivity/-/pipelines)
[![license](https://img.shields.io/badge/license-GNU%20GPLv3%20-green)](https://gitlab.com/eclipse-expeditions/aa-inactivity/-/blob/master/LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![chat](https://img.shields.io/discord/790364535294132234)](https://discord.gg/zmh52wnfvM)

## Content

- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Permissions](#permissions)

## Features

- Automatically notify users who become inactive.
- Automatically notify managers when users become inactive.
- Approval process for leave of absence requests
- Can inform managers about various events via Discord webhook
- List of inactive users
- Define through policies after how many days a user of absence a user is considered inactive
- Fetching the last login dates from Member Audit to determine how long a user has been inactive

Users are notified on Alliance Auth. If you want those notifications to be forwarded as DM on Discord, please check out this app: [Discord Notify](https://gitlab.com/ErikKalkoken/aa-discordnotify).

## Screenshots

A user creating a new leave of absence request:

![request](https://imgpile.com/images/9oMUiC.png)

A manager reviewing a leave of absence request:

![pending](https://imgpile.com/images/9oKyoP.png)

A manager looking through the list of currently inactive and notified users:

![notified](https://imgpile.com/images/9oMIrx.png)

## Installation

### Step 0 - Requirements

This app needs [Member Audit](https://gitlab.com/ErikKalkoken/aa-memberaudit) to function. Please make sure it is installed before continuing.

### Step 1 - Install the Package

Make sure you are in the virtual environment (venv) of your Alliance Auth installation. Then install the newest release from PyPI:

```bash
pip install aa-inactivity
```

### Step 2 - Config

Add `inactivity` to your `INSTALLED_APPS`, and add the following task definition:

```python
CELERYBEAT_SCHEDULE['inactivity_check_inactivity'] = {
    'task': 'inactivity.tasks.check_inactivity',
    'schedule': crontab(minute=0, hour=0),
}
```

### Step 3 - Finalize App Installation

Run migrations:

```bash
python manage.py migrate
python manage.py collectstatic
```

Restart your supervisor services for Auth

## Permissions

This app uses permissions to control access to features.

Name | Purpose | Code
-- | -- | --
general - Can access this app | Enabling the app for a user. This permission should be enabled for everyone who is allowed to use the app |  `basic_access`
general - Can manage leave of absence requests | Allows a user to approve/deny loa requests. |  `manage_leave`
