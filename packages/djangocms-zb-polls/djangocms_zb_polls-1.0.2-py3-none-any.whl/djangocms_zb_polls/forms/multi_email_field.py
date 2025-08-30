#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: "Jhony Alexander Gonzalez Cordoba"
# Date:         21/08/2025 - 9:42 a. m.
# Project:      cms_plugins
# Module Name:  multi_email_field
# Description: 
# ****************************************************************
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

from djangocms_zb_polls.lib import MultiEmailWidget


class MultiEmailField(forms.Field):
    message = _("Enter valid email addresses.")
    code = "invalid"
    widget = MultiEmailWidget

    def to_python(self, value):
        """Normalize data to a list of strings."""
        # Return None if no input was given.
        if not value:
            return []
        return [v.strip() for v in value.splitlines() if v != ""]

    def validate(self, value):
        """Check if value consists only of valid emails."""

        # Use the parent's handling of required fields, etc.
        super(MultiEmailField, self).validate(value)
        try:
            for email in value:
                validate_email(email)
        except ValidationError:
            raise ValidationError(self.message, code=self.code)
