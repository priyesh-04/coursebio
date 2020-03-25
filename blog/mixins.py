from django.contrib.auth.mixins import LoginRequiredMixin

class AccessMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return super().dispatch(request, *args, **kwargs)
            elif request.user.is_admin:
                return super().dispatch(request, *args, **kwargs)
            elif request.user.is_staff:
                return super().dispatch(request, *args, **kwargs)
            else:
                return self.handle_no_permission()
        else:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)