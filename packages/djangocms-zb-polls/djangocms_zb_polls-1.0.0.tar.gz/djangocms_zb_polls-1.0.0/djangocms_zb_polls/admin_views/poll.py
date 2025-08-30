#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: "Jhony Alexander Gonzalez Cordoba"
# Date:         12/08/2025 - 4:13 p. m.
# Project:      cms_plugins
# Module Name:  poll
# Description: 
# ****************************************************************
from django.contrib import admin
from django.urls import path
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from djangocms_zb_polls import views
from djangocms_zb_polls.models import Question, Answer


class QuestionAdminInline(admin.StackedInline):
    model = Question
    extra = 1


class PollAdmin(admin.ModelAdmin):
    list_display = ["title", "email_required", "duplicate_entry", "start_at", "end_at", "options"]
    search_fields = ["title"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [QuestionAdminInline]

    def options(self, obj):
        if Answer.objects.filter(question__poll=obj).exists():
            btn1 = "<a href='{}' class='button'>{}</a>".format(f"answers/download/{obj.id}/", _("Download answers"))
            btn2 = "<a href='{}' class='button'>{}</a>".format(f"answers/send/{obj.id}/", _("Send answers"))
            options_html = format_html(btn1 + "\n" + btn2)
        else:
            options_html = format_html("<span>{}</span>".format(_("The poll has no answers to execute the options.")))
        return options_html

    options.short_description = _("Options")
    options.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        poll_urls = [
            path("answers/download/<int:poll_id>/", views.answers_download, name="polls_answers_download"),
            path("answers/send/<int:poll_id>/", views.answers_send_email, name="polls_answers_send"),
        ]
        return poll_urls + urls
