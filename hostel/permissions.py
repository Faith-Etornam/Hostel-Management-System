from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        
        return obj.user == request.user
    
class IsHostelManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'manager')

    def has_object_permission(self, request, view, obj):
        return obj.hostel == request.user.manager.hostel