from django.urls import re_path

from .views import UserViewModeView

urlpatterns = [
    re_path(
        route=r'^users/(?P<user_id>\d+)/views/modes/$',
        name='user_view_modes', view=UserViewModeView.as_view()
    )
]
