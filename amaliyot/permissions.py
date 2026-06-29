from rest_framework.permissions import BasePermission
from .models import OlympiadParticipant
from .models import Payment
from rest_framework import permissions
from .models import GroupMembership



class IsOlympiadParticipant(BasePermission):
    def has_permission(self, request, view):
        group_id = view.kwargs.get("group_id")
        return OlympiadParticipant.objects.filter(group_id=group_id, user=request.user).exists()


class HasPaidForTest(BasePermission):
    """
    Test pullik bo‘lsa, foydalanuvchi to‘lov qilgan bo‘lishi kerak.
    Bepul testlar uchun hamma kirishi mumkin.
    """
    def has_object_permission(self, request, view, obj):
        
        if not request.user or not request.user.is_authenticated:
            return False

        
        if not getattr(obj, 'is_paid', False):
            return True

        
        return Payment.objects.filter(
            user=request.user,
            test=obj,
            is_successful=True
        ).exists()


class IsTeacherOrAdmin(BasePermission):
    """
    Faqat teacher yoki admin foydalanuvchilarga ruxsat beradi.
    """

    def has_permission(self, request, view):
        
        if request.user and request.user.is_staff:
            return True

        # Teacher rolini foydalanuvchining profilidan tekshirish
        # (masalan, sizda `User` modelida `role` maydoni bo‘lsa)
        if hasattr(request.user, "role") and request.user.role == "teacher":
            return True

        return False



class IsGroupMember(permissions.BasePermission):
    def has_permission(self, request, view):
        group_id = (
            view.kwargs.get('group_pk') or
            view.kwargs.get('group_id') or   
            view.kwargs.get('pk') or
            request.data.get('group')
        )

        if view.action in ['create', 'list']:
            if not group_id:
                return False

            return GroupMembership.objects.filter(
                group_id=group_id,
                user=request.user
            ).exists()

        return True

    def has_object_permission(self, request, view, obj):
        return GroupMembership.objects.filter(
            group=obj.group,
            user=request.user
        ).exists()







