#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

from django.contrib import admin

from djangocms_zb_polls.admin_views import PollAdmin, QuestionAdmin, AnswerAdmin
from djangocms_zb_polls.models import Poll, Question, Answer

# Register your models here.

admin.site.register(Poll, PollAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
