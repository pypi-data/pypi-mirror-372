#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

from cms.models import CMSPlugin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models

from djangocms_zb_polls.lib import MultiEmailField, TypeFieldEnum


# Create your models here.

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Poll(BaseModel):
    title = models.CharField(max_length=200, null=False, blank=False, verbose_name=_("Title"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Description"))
    email_required = models.BooleanField(default=False, verbose_name=_("Email Required"),
                                         help_text=_("If true, the email is required to respond."))
    duplicate_entry = models.BooleanField(_("Multiple submissions"), default=False,
                                          help_text=_("If True, email can resubmit."))
    notification_to = MultiEmailField(blank=True, null=True, verbose_name=_("Notification to"),
                                      help_text=_("Enter one or more email addresses to receive form submission "
    "notifications. Enter each address on a separate line, without using commas or spaces to separate them."))
    start_at = models.DateTimeField(null=True, blank=True, default=timezone.now, verbose_name=_("Start date"),
                                    help_text=_("Start date to allow for responses to be submitted."))
    end_at = models.DateTimeField(null=True, blank=True, verbose_name=_("End date"),
                                  help_text=_("End date to allow for responses to be submitted."))

    class Meta:
        verbose_name = _("Poll")
        verbose_name_plural = _("Polls")

    def __str__(self):
        return self.title

    @property
    def published(self):
        published = True
        now = timezone.now()
        if self.start_at is not None and self.start_at > now:
            published = False
        if self.end_at is not None and self.end_at < now:
            published = False
        return published

    def clean(self):
        if self.end_at is not None and self.end_at < self.start_at:
            raise ValidationError(
                _("The end date must be greater than the start date of the publication."))


class Question(BaseModel):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, verbose_name=_("Poll"), related_name="questions",
                             related_query_name="question")
    label = models.CharField(max_length=500, null=False, blank=False, verbose_name=_("Label"),
                             help_text=_("Enter your question in here."))
    type_field = models.PositiveSmallIntegerField(choices=TypeFieldEnum.choices, verbose_name=_("Type of field"))
    options = models.TextField(null=True, blank=True, verbose_name=_("Options"), help_text=_(
        "If type of field is radio, select, multi select or rating, fill in the options separated "
        "by pipe (|). Ex: Male|Female."))
    help_text = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Help Text"),
                                 help_text=_("You can add a help text in here.")
                                 )
    required = models.BooleanField(default=True, verbose_name=_("Required"),
                                   help_text=_("If True, the user must provide an answer to this question."))
    ordering = models.PositiveIntegerField(default=0, verbose_name=_("Ordering"),
                                           help_text=_("Defines the question order within the polls."))
    extra_options = models.JSONField(null=True, blank=True, verbose_name=_("Extra Options"), default=dict, help_text=_(
        'Additional options to be added to the form field. For example: {"minlength": 4, "maxlength": 8, "disabled":true}'))

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ("ordering",)

    def __str__(self):
        return f"{self.poll}: {self.label}"

    def clean(self):
        if not self.extra_options:
            self.extra_options = {}
        if self.type_field in [TypeFieldEnum.MULTISELECT, TypeFieldEnum.RADIO,
                               TypeFieldEnum.SELECT, TypeFieldEnum.RATING]:
            if not self.options:
                raise ValidationError({"options": _("For this type of question add at least one option.")})
        else:
            if self.options:
                raise ValidationError({"options": _("For this type of question you do not require options.")})


class Answer(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_("Question"), related_name="answers",
                                 related_query_name="answer")
    value = models.TextField(null=True, blank=True, verbose_name=_("Value"),
                             help_text=_("The value of the answer given by the user."))
    email = models.EmailField(null=True, blank=True, verbose_name=_("User Email."), )

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
        ordering = ("question__ordering",)

    def __str__(self):
        return f"{self.question}: {self.value}"

    def clean(self):
        if self.question.poll.email_required:
            if not self.email:
                raise ValidationError({"email": _("Email required for this question.")})
            if not self.question.poll.duplicate_entry and Answer.objects.filter(question=self.question,
                                                                                email__exact=self.email).exists():
                raise ValidationError({"email": _("There is already a reply with the same email.")})


class PluginConfig(CMSPlugin):
    TEMPLATES_CHOICES = [
        ('default', _('Default')),
    ]
    TEMPLATES_CHOICES += getattr(
        settings,
        'DJANGOCMS_ZB_POLLS_TEMPLATES',
        [],
    )
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, verbose_name=_("Poll"),
                             help_text=_("Poll form you want to display."), related_name="plugins",
                             related_query_name="plugin")
    template = models.CharField(_("Template"), max_length=250, choices=TEMPLATES_CHOICES,
                                default=TEMPLATES_CHOICES[0][0],
                                help_text=_("(HTML) Alternative template for the design of complement."))
