#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: "Jhony Alexander Gonzalez Cordoba"
# Date:         21/08/2025 - 9:57 a. m.
# Project:      cms_plugins
# Module Name:  send_answers_from
# Description: 
# ****************************************************************
from django import forms
from django.utils.translation import gettext_lazy as _
from zibanu.django.lib import Email

from djangocms_zb_polls.forms import MultiEmailField
from djangocms_zb_polls.lib.get_file_excel_answers import get_file_excel_answers
from djangocms_zb_polls.models import Poll


class SendAnswersForm(forms.Form):
    email = MultiEmailField(label=_("Email address"), required=True, help_text=_("Enter valid email addresses."))

    def __init__(self, poll_id=None, *args, **kwargs):
        self.poll = Poll.objects.get(pk=poll_id) if poll_id is not None else None
        super().__init__(*args, **kwargs)

    def save(self):
        b_return = False
        try:
            cleaned_data = super().clean()
            excel_file, filename = get_file_excel_answers(poll_id=self.poll.id)
            if excel_file is not None and filename is not None:
                b_return = True
                email_context = {
                    "poll_title": self.poll.title,
                }
                email = Email(
                    subject=_("Poll report (%(title)s)") % {"title": self.poll.title},
                    to=cleaned_data["email"],
                )
                email.set_text_template("djangocms_zb_polls/mail/poll_report_responses.txt", context=email_context)
                email.attach(filename, excel_file.read(),
                             'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                email.send()
            else:
                raise forms.ValidationError(_("The poll has no answers to execute the options."))
        except forms.ValidationError as e:
            self.add_error(None, e)
        return b_return
