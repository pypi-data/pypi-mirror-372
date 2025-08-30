#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class DjangocmsZbPollsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djangocms_zb_polls'
    verbose_name = _('Django CMS ZB Polls')

    def ready(self):
        # validators
        field_validator = {
            'min_length': {
                'email': 1,
                'text': 1,
                'text_area': 1,
            },
            'max_length': {
                'email': 150,
                'text': 250,
                'text_area': 1000,
            }
        }
        settings.DJANGO_CMS_ZB_POLLS_FIELD_VALIDATORS = getattr(settings, 'DJANGO_CMS_ZB_POLLS_FIELD_VALIDATORS',
                                                                field_validator)
