# gs-django-authplus

Reusable Django application `authplus` provides structured permission grouping.

When having a lot of defined models, managing permissions for users and groups can be quite a challenge. This application allows organizing permissions into permission packages, just like users are organized into groups. This makes it more natural than using groups for everything.

Organizing user groups into subgroups is also provided. User that is a member of a group is also member of all parent groups of that group.

## Installation

If using Astral's uv for virtual environment and project dependencies:

```
$ uv add gs-django-authplus
```

Or, with pip in your virtual environment:

```
$ pip install gs-django-authplus
```


## Quick setup

Add application to `settings.py`:

```
INSTALLED_APPS = [
    ...
    "authplus",
]
```


## Models

### PermissionsPackage

Permissions package is a generic way to categorize permissions.

Permissions packages are used for easier applying a bunch of related permissions to a user or user groups. This can also be achieved using `django.contrib.auth.models.Group`, but it seems more natural to separate permission groups and user groups.

`PermissionPackage` is based on abstract class `AbstractPermissionsPackage` to allow easier extension and customizations.


### UserGroup

User group is a generic way to categorize users.

User groups have a hierarchical structure so each group can have several subgroups. User that is a member of a group is also member of all parent groups of that group.

Permissions for user groups can be granted using individual permissions or permissions packages.

`UserGroup` is based on abstract class `AbstractUserGroup` to allow easier extension and customizations.


### AbstractUserPlus

Abstract class for project user which inherits from class `django.contrib.auth.models.AbstractUser` and allows using `PermissionsPackage` and `UserGroup` for defining permissions granted to user.


### User

Project user based on `AbstractUserPlus`.


## Translations

Package comes with translations to:

- Croatian (hr)

To create translations for new language:

```bash
$ git clone git@gitlab.com:gs-django-authplus.git
$ cd gs-django-authplus
$ uv sync
$ uv run django-admin makemessages -l language_code
# edit django.po file for the new language
$ make compilemessages
# build will also automatically compile messages
$ uv build
```
