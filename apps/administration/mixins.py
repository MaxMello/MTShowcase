from django.shortcuts import get_object_or_404
from django.views.generic import View

from apps.user.models import User


class ProfAdminPermissionMixin(View):
    enter_allowed = False

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            user = get_object_or_404(User, pk=request.user.id)
            if user.type == User.PROF or user.type == User.ADMIN:
                self.enter_allowed = True

        return super(ProfAdminPermissionMixin, self).dispatch(request, *args, **kwargs)
