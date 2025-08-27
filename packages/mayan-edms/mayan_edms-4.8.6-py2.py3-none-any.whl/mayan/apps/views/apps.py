from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from mayan.apps.app_manager.apps import MayanAppConfig
from mayan.apps.common.menus import menu_list_facet
from mayan.apps.navigation.source_columns import SourceColumn

from .links import link_user_view_modes


class ViewsApp(MayanAppConfig):
    app_namespace = 'views'
    app_url = 'views'
    has_tests = True
    name = 'mayan.apps.views'
    verbose_name = _(message='Views')

    def ready(self):
        super().ready()

        UserViewMode = self.get_model(model_name='UserViewMode')
        User = get_user_model()

        SourceColumn(
            attribute='get_app_config', include_label=True,
            source=UserViewMode
        )
        SourceColumn(
            attribute='name', is_identifier=True, source=UserViewMode
        )
        SourceColumn(
            attribute='get_value_display', include_label=True,
            source=UserViewMode
        )

        menu_list_facet.bind_links(
            links=(
                link_user_view_modes,
            ), sources=(User,)
        )
