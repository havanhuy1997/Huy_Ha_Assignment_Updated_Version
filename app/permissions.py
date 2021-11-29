import rest_framework.permissions as rest_permissions


class isObjectBelongToUser(rest_permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.user.id
