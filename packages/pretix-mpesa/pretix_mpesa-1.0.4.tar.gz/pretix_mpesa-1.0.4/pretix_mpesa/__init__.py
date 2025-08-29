from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class PluginApp(AppConfig):
    name = 'pretix_mpesa'
    verbose_name = 'Mpesa mobile payments'

    class PretixPluginMeta:
        name = gettext_lazy('Mpesa mobile payments')
        author = 'Emmanuel Nyachoke'
        description = gettext_lazy('Adds safaricom mpesa payments to pretix')
        visible = True
        version = '1.0.0'

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'pretix_mpesa.PluginApp'
