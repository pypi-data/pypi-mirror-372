#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: "Jhony Alexander Gonzalez Cordoba"
# Date:         15/08/2025 - 2:30 p. m.
# Project:      cms_plugins
# Module Name:  template_tags
# Description: 
# ****************************************************************
from django.template import Library

register = Library()


@register.filter(name='widgetaddclass')
def widgetaddclass(field, class_attr):
    return field.as_widget(attrs={'class': class_attr})


@register.filter(name='widgetaddstyle')
def widgetaddstyle(field, style_attr):
    return field.as_widget(attrs={'style': style_attr})
