#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: "Jhony Alexander Gonzalez Cordoba"
# Date:         12/08/2025 - 4:22 p. m.
# Project:      cms_plugins
# Module Name:  question
# Description: 
# ****************************************************************
from django.contrib import admin


class QuestionAdmin(admin.ModelAdmin):
    list_display = ["poll", "label", "type_field", "required", "ordering"]
    readonly_fields = ["poll", "label", "type_field", "required", "ordering", "options", "extra_options", "created_at",
                       "updated_at"]
    search_fields = ["poll__title", "label"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def change_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context["show_delete"] = False
        return super().change_view(request, object_id, form_url, extra_context)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions