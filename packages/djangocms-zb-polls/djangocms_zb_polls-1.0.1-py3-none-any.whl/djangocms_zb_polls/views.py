#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from djangocms_zb_polls.forms import SendAnswersForm
from djangocms_zb_polls.lib import get_file_excel_answers


def answers_download(request, poll_id):
    """
    View download answers Excel file.
    :param request: Request object.
    :param poll_id: ID Poll.
    :return: Response.
    """
    excel_file, filename = get_file_excel_answers(poll_id=poll_id)
    if excel_file is not None and filename is not None:
        # Crea la respuesta HTTP con el tipo de contenido correcto
        response = HttpResponse(excel_file.getvalue(),
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f"attachment; filename={filename}"
    else:
        messages.warning(request, _("The poll has no answers to execute the options."))
        response = redirect("/admin/djangocms_zb_polls/poll")
    return response


def answers_send_email(request, poll_id):
    """
    View send Email answers Excel file.
    :param request: Request object.
    :param poll_id: ID Poll.
    :return: None.
    """
    form = SendAnswersForm()
    if request.method == 'POST':
        form = SendAnswersForm(poll_id=poll_id, data=request.POST)
        if form.is_valid():
            save = form.save()
            if save:
                messages.success(request, _("Email sent successfully."))
                form = SendAnswersForm()
    context = dict(
        {"form": form},
    )
    return TemplateResponse(request, "djangocms_zb_polls/send_answers.html", context)
