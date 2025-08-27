from django.utils.translation import gettext_lazy as _

from mayan.apps.user_management.permissions import permission_user_view
from mayan.apps.user_management.querysets import get_user_queryset
from mayan.apps.user_management.views.view_mixins import (
    DynamicExternalUserViewMixin
)
from mayan.apps.views.view_mixins import ExternalObjectViewMixin

from .icons import icon_user_view_modes
from .generics import SingleObjectListView


class UserViewModeView(
    DynamicExternalUserViewMixin, ExternalObjectViewMixin,
    SingleObjectListView
):
    external_object_permission = permission_user_view
    external_object_pk_url_kwarg = 'user_id'
    view_icon = icon_user_view_modes

    def get_external_object_queryset(self):
        return get_user_queryset(user=self.request.user)

    def get_extra_context(self):
        return {
            'hide_link': True,
            'hide_object': True,
            'no_results_icon': icon_user_view_modes,
            'no_results_text': _(
                message='View modes control the format used to display a '
                'collection of objects.'
            ),
            'no_results_title': _(message='No view modes available'),
            'object': self.external_object,
            'title': _(
                message='Persistent view modes for user: %s'
            ) % self.external_object
        }

    def get_source_queryset(self):
        return self.external_object.view_modes.all()
