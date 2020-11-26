from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """
    Permission for checking the request user is the owner or a superuser
    """
    message = "In order to access, " \
              "you must be the owner of the profile."

    def has_permission(self, request, view):
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class ContentPermission(BasePermission):
    """
    Permission for Content API endpoint.
    If `POST` is approved (published), Reporter user is allowed only for
        `SAFE METHODS`

    Approved Posts can be deleted by only Superuser
    """

    def has_permission(self, request, view):
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):

        if obj.post.is_approved and request.method in ('PUT', 'PATCH'):
            return request.user.is_staff and request.user.user_type in (3, 4)
        elif obj.post.is_approved and request.method == 'DELETE':
            return request.user.is_staff and request.user.user_type == 4
        return request.user.is_staff


class FeedbackPermission(BasePermission):
    """
    Permission for Feedback API endpoint.
    `SAFE METHODS` and `POST`are allowed for any admin user
    `PUT`, `PATCH`, `DELETE` methods are allowed for only the `OWNER`
    """

    def has_permission(self, request, view):
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_staff
        return obj.owner == request.user


class IsCustomAdminUser(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_staff and request.user.user_type == 4:
            return True


class IsEditorUserOrCustomAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff and request.user.user_type in (3, 4)


class IsReporterUser(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff and request.user.user_type == 2


class IsProfileOwnerOrCustomAdminUser(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.user_type == 4
