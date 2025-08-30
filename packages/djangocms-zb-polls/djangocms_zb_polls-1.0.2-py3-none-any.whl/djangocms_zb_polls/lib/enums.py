#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: "Jhony Alexander Gonzalez Cordoba"
# Date:         12/08/2025 - 3:12 p. m.
# Project:      cms_plugins
# Module Name:  enums
# Description: 
# ****************************************************************
from django.db import models
from django.utils.translation import gettext_lazy as _


class TypeFieldEnum(models.IntegerChoices):
    TEXT = 0, _("Text")
    NUMBER = 1, _("Number")
    RADIO = 2, _("Radio")
    SELECT = 3, _("Select")
    MULTISELECT = 4, _("Multi Select")
    TEXTAREA = 5, _("Text Area")
    EMAIL = 6, _("Email")
    DATE = 7, _("Date")
    RATING = 8, _("Rating")
