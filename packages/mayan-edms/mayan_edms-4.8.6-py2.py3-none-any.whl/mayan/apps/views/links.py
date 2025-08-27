from django.utils.translation import gettext_lazy as _

from mayan.apps.authentication.link_conditions import (
    condition_user_is_authenticated
)
from mayan.apps.navigation.links import Link

from .icons import icon_user_view_modes

link_user_view_modes = Link(
    condition=condition_user_is_authenticated,
    kwargs={'user_id': 'resolved_object.pk'}, icon=icon_user_view_modes,
    text=_(message='View modes'), view='views:user_view_modes'
)
