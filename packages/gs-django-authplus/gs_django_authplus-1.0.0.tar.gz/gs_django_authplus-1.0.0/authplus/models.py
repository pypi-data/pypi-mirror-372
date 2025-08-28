from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.contrib.auth.models import AbstractUser, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class AbstractPermissionsPackage(models.Model):
    """
    Permissions package is a generic way to categorize permissions.

    Permissions packages are used for easier applying a bunch of
    related permissions to a user or user groups. This can also be
    achieved using django.contrib.auth.models.Group, but it seems more
    natural to separate permission groups and user groups.

    Permissions related to package that are granted to a user are put
    into permissions field of a user on granting a package, rather than
    using recursive method when trying to determine whether user has
    particular permission. All the work is done on assigning permissions
    rather than on retrieval.

    This is an abstract class to allow extension and customizations.

    Defines fields:

    - name - Name of permissions package.
    - description - Description of permissions package.
    - permissions - Permissions included in the package.

    Defines methods:

    - get_users() - Get direct users of this permissions package.
    - get_all_users() - Get all users that have this permissions package
                        (including users of supergroups).
    - update_users() - Update permissions for all users that have this
                       permissions package.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("name"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
    )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="%(class)s_set",
        verbose_name=_("permissions"),
        help_text=_("Permissions included in the package."),
    )

    class Meta:
        """Meta class."""

        abstract = True
        verbose_name = _("permissions package")
        verbose_name_plural = _("permissions packages")

    def __str__(self) -> str:
        """
        Object representation as string.

        Returns:
            str: The name of the object.

        """
        return self.name

    def get_users(self) -> set[AbstractUserPlus]:
        """
        Get direct users of this permissions package.

        Returns:
            set[AbstractUserPlus]: A set of direct users of the permissions package.

        """
        users: set[AbstractUserPlus] = set()

        for related_object in self._meta.get_fields():
            if isinstance(related_object, models.ManyToManyRel) and related_object.name.endswith("_set"):
                related_model = related_object.related_model
                if isinstance(related_model, type) and issubclass(related_model, AbstractUserPlus):
                    users.update(getattr(self, related_object.name).all())

        return users

    def get_all_users(self) -> set[AbstractUserPlus]:
        """
        Get all users that have this permissions package (including users of supergroups).

        This method retrieves all users associated with this permissions
        package. It includes users from direct groups as well as users
        from all supergroups of those groups that have this permissions package.

        Returns:
            set[AbstractUser]: A set of all users that have this permissions package.

        """
        all_users: set[AbstractUserPlus] = self.get_users()

        # It is more efficient to get all groups first and get their direct users,
        # than to get all users of all groups (which goes through supergroups again).
        groups: set[UserGroup] = set(self.usergroup_set.all())  # type: ignore[attr-defined]
        all_groups: set[UserGroup] = set(groups)
        for group in groups:
            all_groups.update(group.get_all_supergroups())

        # Get all users that are in supergroups of this group
        for group in all_groups:
            all_users.update(group.get_users())

        return all_users

    def update_users(self) -> None:
        """Update permissions for all users that have this permissions package."""
        for user in self.get_all_users():
            user.update_permissions()


class PermissionsPackage(AbstractPermissionsPackage):
    """
    Permissions package.

    Inherits fields:

    - name [AbstractPermissionsPackage]
    - description [AbstractPermissionsPackage]
    - permissions [AbstractPermissionsPackage]

    Inherits methods:

    - get_users() [AbstractPermissionsPackage]
    - get_all_users() [AbstractPermissionsPackage]
    - update_users() [AbstractPermissionsPackage]
    """


class AbstractUserGroup(models.Model):
    """
    User group is a generic way to categorize users.

    User groups have a hierarchical structure so each group can have several
    subgroups. User that is a member of a group is also member of all parent
    groups of that group.

    Permissions for user groups can be granted using individual
    permissions or permissions packages.

    Permissions related to user as a member of different user groups are
    determined (put into permissions field of a user) on defining user group
    membership, rather than using recursive method when trying to determine
    whether user has particular permission. All the work is done on assigning
    permissions rather than on retrieval.

    This is an abstract class to allow extension.

    Defines fields:

    - name - Name of user group.
    - description - Description of user group.
    - subgroups - Subgroups of user group.
    - permissions_packages - Permissions packages granted to user group.
    - permissions - Permissions granted to user group.

    Defines methods:

    - get_all_subgroups(catalog) - Get all subgroups of this user group.
    - get_all_supergroups(catalog) - Get all supergroups of this user group.
    - get_users() - Get direct users of this user group.
    - get_all_users() - Get all users that have this user group
                        (including users of supergroups).
    - update_users() - Update permissions for all users that have this user
                       group.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("name"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
    )
    subgroups = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="%(class)s_set",
        verbose_name=_("subgroups"),
    )
    permissions_packages = models.ManyToManyField(
        PermissionsPackage,
        blank=True,
        related_name="%(class)s_set",
        verbose_name=_("permissions packages"),
    )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="%(class)s_set",
        verbose_name=_("individual permissions"),
    )

    class Meta:
        """Meta class."""

        abstract = True
        verbose_name = _("user group")
        verbose_name_plural = _("user groups")

    def __str__(self) -> str:
        """
        Return the name of the object as a string.

        Returns:
            str: The name of the object.

        """
        return self.name

    def get_all_subgroups(self, catalog: set[UserGroup] | None = None) -> set[UserGroup]:
        """
        Get all subgroups of this user group.

        This method is recursive and returns all subgroups of the user
        group, not just the direct subgroups.

        Args:
            catalog: A set of user groups that have already been processed.
                This argument is optional and will be created if not provided.

        Returns:
            set[AbstractUserGroup]: A set of all subgroups of the user group.

        """
        if catalog is None:
            catalog = set()
        for subgroup in self.subgroups.all():
            if subgroup not in catalog:
                catalog.add(subgroup)  # type: ignore[arg-type]
                subgroup.get_all_subgroups(catalog)
        return catalog

    def get_all_supergroups(self, catalog: set[UserGroup] | None = None) -> set[UserGroup]:
        """
        Get all supergroups of this user group.

        This method is recursive and returns all supergroups of the user
        group, not just the direct supergroups.

        Args:
            catalog: A set of user groups that have already been processed.
                     This argument is optional and will be created if not
                     provided.

        Returns:
            set[AbstractUserGroup]: A set of all supergroups of the user group.

        """
        if catalog is None:
            catalog = set()
        for supergroup in UserGroup.objects.filter(subgroups=self):  # type: ignore[misc]
            if supergroup not in catalog:
                catalog.add(supergroup)
                supergroup.get_all_supergroups(catalog)
        return catalog

    def get_users(self) -> set[AbstractUserPlus]:
        """
        Get direct users of this user group.

        Returns:
            set[AbstractUserPlus]: A set of direct users of this user group.

        """
        users: set[AbstractUserPlus] = set()

        for related_object in self._meta.get_fields():
            if isinstance(related_object, models.ManyToManyRel) and related_object.name.endswith("_set"):
                related_model = related_object.related_model
                if isinstance(related_model, type) and issubclass(related_model, AbstractUserPlus):
                    users.update(getattr(self, related_object.name).all())

        return users

    def get_all_users(self) -> set[AbstractUserPlus]:
        """
        Get all users that have this user group (including users of supergroups).

        This method is recursive and returns all users that have this user
        group, not just the direct users. It does this by finding all
        supergroups of this user group and then finding all users of those
        supergroups.

        Returns:
            set[AbstractUserPlus]: A set of all users that have this user group.

        """
        all_users: set[AbstractUserPlus] = self.get_users()
        all_groups = self.get_all_supergroups()

        # Get all users that are in supergroups of this group
        for group in all_groups:
            all_users.update(group.get_users())

        return all_users

    def update_users(self) -> None:
        """Update permissions for all users that have this user group."""
        for user in self.get_all_users():
            user.update_permissions()


class UserGroup(AbstractUserGroup):
    """
    User group.

    Inherits fields:

    - name [AbstractUserGroup]
    - description [AbstractUserGroup]
    - subgroups [AbstractUserGroup]
    - permissions_packages [AbstractUserGroup]
    - permissions [AbstractUserGroup]

    Inherits methods:

    - get_all_subgroups(catalog) [AbstractUserGroup]
    - get_all_supergroups(catalog) [AbstractUserGroup]
    - get_users() [AbstractUserGroup]
    - get_all_users() [AbstractUserGroup]
    - update_users() [AbstractUserGroup]
    """


class AbstractUserPlus(AbstractUser):
    """
    Abstract class for project user.

    Allows using `PermissionsPackage` and `UserGroup` for defining permissions granted to user.

    Defines fields:

    - user_groups - The groups this user belongs to. A user will get all
                    permissions granted to each of his groups.
    - permissions_packages - The permissions packages this user is granted.
                             A user will get all permissions granted to each
                             of his permissions packages.
    - individual_permissions - Additional individual permissions this user is
                               granted.

    Inherites fields:

    - date_joined [auth.models.AbstractUser]
    - email [auth.models.AbstractUser]
    - first_name [auth.models.AbstractUser]
    - groups [auth.models.PermissionsMixin]
    - is_active [auth.models.AbstractUser]
    - is_staff [auth.models.AbstractUser]
    - is_superuser [auth.models.PermissionsMixin]
    - last_login [auth.base_user.AbstractBaseUser]
    - last_name [auth.models.AbstractUser]
    - password [auth.base_user.AbstractBaseUser]
    - user_permissions [auth.models.PermissionsMixin]
    - username [auth.models.AbstractUser]

    Defines methods:

    - get_usergroups() - Get all user groups associated with this user.
                         This method collects all direct user groups and
                         their subgroups.
    - get_permissions() - Get all permissions associated with this user.
    - update_permissions() - Update permissions for this user.

    Inherits methods:

    - has_perm(perm, obj) [auth.models.PermissionsMixin]
    - has_perms(perms, obj) [auth.models.PermissionsMixin]
    - has_module_perms(app_label) [auth.models.PermissionsMixin]
    - get_user_permissions(obj) [auth.models.PermissionsMixin]
    - get_all_permissions(obj) [auth.models.PermissionsMixin]
    - get_full_name() [auth.base_user.AbstractUser]
    - get_short_name() [auth.base_user.AbstractUser]
    - email_user(subject, message, from_email) [auth.base_user.AbstractUser]
    - set_password(raw_password) [auth.base_user.AbstractBaseUser]
    - check_password(raw_password) [auth.base_user.AbstractBaseUser]
    - set_unusable_password() [auth.base_user.AbstractBaseUser]
    - has_usable_password() [auth.base_user.AbstractBaseUser]
    - get_session_auth_hash() [auth.base_user.AbstractBaseUser]
    """

    user_groups = models.ManyToManyField(
        UserGroup,
        blank=True,
        related_name="%(class)s_set",
        verbose_name=_("user groups"),
        help_text=_("The groups this user belongs to. A user will get all permissions granted to each of his groups."),
    )
    permissions_packages = models.ManyToManyField(
        PermissionsPackage,
        blank=True,
        related_name="%(class)s_set",
        verbose_name=_("permissions packages"),
        help_text=_(
            "Permissions packages this user is granted. A user will get all "
            "permissions that are in the permissions package.",
        ),
    )
    individual_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name="individual_%(class)s_set",
        verbose_name=_("individual permissions"),
        help_text=_("Additional individual permissions this user is granted."),
    )

    class Meta:
        """Meta class."""

        abstract = True
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def get_usergroups(self) -> set[UserGroup]:
        """
        Get all user groups associated with this user.

        This method collects all direct user groups and their subgroups.

        Returns:
            set[AbstractUserGroup]: A set of all user groups including subgroups.

        """
        all_groups: set[UserGroup] = set()
        user_groups: models.QuerySet[UserGroup] = self.user_groups.all()
        for group in user_groups:
            all_groups.update(group.get_all_subgroups(all_groups))
        all_groups.update(user_groups)
        return all_groups

    def get_permissions(self) -> set[Permission]:
        """
        Get all permissions associated with this user.

        This method collects all individual permissions, permissions from
        permissionspackages, and permissions from all user groups including
        subgroups.

        Returns:
            set[Permission]: A set of all permissions.

        """
        all_permissions = set(self.individual_permissions.all())
        all_packages = set(self.permissions_packages.all())
        all_groups = set(self.get_usergroups())
        for group in all_groups:
            all_packages.update(group.permissions_packages.all())
            all_permissions.update(group.permissions.all())
        for package in all_packages:
            all_permissions.update(package.permissions.all())
        return all_permissions

    def update_permissions(self) -> None:
        """Update permissions for this user."""
        self.user_permissions.set(self.get_permissions())


class User(AbstractUserPlus):
    """
    Project user.

    Inherits fields:

    - date_joined [auth.models.AbstractUser]
    - email [auth.models.AbstractUser]
    - first_name [auth.models.AbstractUser]
    - groups [auth.models.PermissionsMixin]
    - is_active [auth.models.AbstractUser]
    - is_staff [auth.models.AbstractUser]
    - is_superuser [auth.models.PermissionsMixin]
    - last_login [auth.base_user.AbstractBaseUser]
    - last_name [auth.models.AbstractUser]
    - password [auth.base_user.AbstractBaseUser]
    - user_permissions [auth.models.PermissionsMixin]
    - username [auth.models.AbstractUser]
    - user_groups [AbstractUserPlus]
    - permissions_packages [AbstractUserPlus]
    - individual_permissions [AbstractUserPlus]

    Inherits methods:

    - has_perm(perm, obj) [auth.models.PermissionsMixin]
    - has_perms(perms, obj) [auth.models.PermissionsMixin]
    - has_module_perms(app_label) [auth.models.PermissionsMixin]
    - get_user_permissions(obj) [auth.models.PermissionsMixin]
    - get_all_permissions(obj) [auth.models.PermissionsMixin]
    - get_full_name() [auth.base_user.AbstractUser]
    - get_short_name() [auth.base_user.AbstractUser]
    - email_user(subject, message, from_email) [auth.base_user.AbstractUser]
    - set_password(raw_password) [auth.base_user.AbstractBaseUser]
    - check_password(raw_password) [auth.base_user.AbstractBaseUser]
    - set_unusable_password() [auth.base_user.AbstractBaseUser]
    - has_usable_password() [auth.base_user.AbstractBaseUser]
    - get_session_auth_hash() [auth.base_user.AbstractBaseUser]
    - get_usergroups() [AbstractUserPlus]
    - get_permissions() [AbstractUserPlus]
    - update_permissions() [AbstractUserPlus]
    """
