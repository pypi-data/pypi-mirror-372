from rest_framework import permissions


class UserModificationPermission(permissions.BasePermission):
    """
    Custom permission to only allow admins or the user themselves to edit their information.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the user of the profile or admin
        return obj == request.user or request.user.is_staff
