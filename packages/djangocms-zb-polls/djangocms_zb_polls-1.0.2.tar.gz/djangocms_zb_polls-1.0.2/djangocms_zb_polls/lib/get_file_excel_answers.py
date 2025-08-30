#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: "Jhony Alexander Gonzalez Cordoba"
# Date:         21/08/2025 - 12:12 p. m.
# Project:      cms_plugins
# Module Name:  get_answers_excel
# Description: 
# ****************************************************************
from io import BytesIO

import pandas as pd
from django.utils.translation import gettext_lazy as _


def get_file_excel_answers(poll_id):
    """
    Method create in memory file excel answers database.
    :param poll_id: ID Poll.
    :return: excel Fle and Filename.
    """
    excel_file = None
    filename = None
    from djangocms_zb_polls.models import Answer, Poll
    poll = Poll.objects.get(pk=poll_id)
    queryset = Answer.objects.filter(question__poll=poll).order_by("id")
    if queryset:
        answers = list(queryset.values("id", "question_id", "question__label", "value", "email", "created_at"))
        df = pd.DataFrame(list(answers))
        if not df.empty:
            if "created_at" in df.columns:
                df["created_at"] = df["created_at"].dt.tz_localize(None)
                df["Date"] = pd.to_datetime(df["created_at"])
                df.pop("created_at")
        # Crear un objeto BytesIO para guardar el archivo en memoria
        excel_file = BytesIO()
        header = [_("ID"), _("Question ID"), _("Question Label"), _("Answer"), _("Email"), _("Created At")]
        df.to_excel(excel_file, index=False, sheet_name='Answers', header=header)
        excel_file.seek(0)
        poll_title = poll.title.lower().replace(" ", "_")
        filename = f"{poll_title}.xlsx"
    return excel_file, filename
