#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: "Jhony Alexander Gonzalez Cordoba"
# Date:         12/08/2025 - 2:51 p. m.
# Project:      cms_plugins
# Module Name:  fields
# Description: 
# ****************************************************************
from django.db import models

class MultiEmailField(models.Field):
    description = "A multi e-mail field stored as a multi-lines text"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", [])
        super(MultiEmailField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        from djangocms_zb_polls.forms.multi_email_field import MultiEmailField as MultiEmailFormField
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {"form_class": MultiEmailFormField}
        defaults.update(kwargs)
        return super(MultiEmailField, self).formfield(**defaults)

    def from_db_value(self, value, expression, connection, context=None):
        if value is None:
            return []
        return value.splitlines()

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, str):
            return value
        elif isinstance(value, list):
            return "\n".join(value)

    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        return value.splitlines()

    def get_internal_type(self):
        return "TextField"
