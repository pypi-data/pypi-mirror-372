from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class Oauth2Config(AppConfig):
    name = 'mad_oauth2'
    verbose_name = 'Mad OAuth2'

    def ready(self):
        import mad_oauth2.signals