from rest_framework import permissions

MESSAGE = "In order to access to this object, you must be the owner"


class CommentOwner(permissions.BasePermission):
    """
    Permission for checking the request user is the comment owner
    """
    message = MESSAGE

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.commented_by.id == request.user.id


class CommentOwnerOrIsAdmin(permissions.BasePermission):
    """
    Permission for checking the request user is the comment owner or admin user
    """
    message = MESSAGE

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.commented_by.id == request.user.id or \
               request.user.user_type == 4


class IsOwner(permissions.BasePermission):
    """
    Permission for checking the request user is the owner
    """
    message = MESSAGE

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj == request.user
