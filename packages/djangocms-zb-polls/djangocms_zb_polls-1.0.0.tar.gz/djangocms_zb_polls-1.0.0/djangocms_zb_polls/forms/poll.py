#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: "Jhony Alexander Gonzalez Cordoba"
# Date:         13/08/2025 - 4:47 p. m.
# Project:      cms_plugins
# Module Name:  polls
# Description: 
# ****************************************************************
from typing import List, Tuple

from django import forms
from django.conf import settings
from django.core.mail import BadHeaderError
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from zibanu.django.lib import Email

from djangocms_zb_polls.lib import TypeFieldEnum
from djangocms_zb_polls.models import Question, Answer


def make_options(question: Question) -> List[Tuple[str, str]]:
    options = []
    for option in question.options.split('|'):
        option = option.strip()
        options.append((option, option))
    return options


class PollForm(forms.Form):

    def __init__(self, poll, *args, **kwargs):
        self.poll = poll
        self.field_names = []
        self.questions = self.poll.questions.all().order_by('ordering')
        super().__init__(*args, **kwargs)
        self.settings_app_validators = settings.DJANGO_CMS_ZB_POLLS_FIELD_VALIDATORS

        if self.poll.email_required:
            field_name = f'email'
            self.fields[field_name] = forms.EmailField(label="Email", required=True,
                                                       help_text=_("Required to save answers."))
            self.fields[field_name].widget.attrs.update(autocomplete="on")
            if not self.poll.published:
                self.fields[field_name].disabled = True
            self.field_names.append(field_name)
        for question in self.questions:
            # to generate field name
            field_name = f'field_zb_polls_{question.id}'
            if question.type_field == TypeFieldEnum.MULTISELECT:
                choices = make_options(question)
                self.fields[field_name] = forms.MultipleChoiceField(choices=choices, label=question.label,
                                                                    widget=forms.CheckboxSelectMultiple, )
            elif question.type_field == TypeFieldEnum.RADIO:
                choices = make_options(question)
                self.fields[field_name] = forms.ChoiceField(choices=choices, label=question.label,
                                                            widget=forms.RadioSelect)
            elif question.type_field == TypeFieldEnum.SELECT:
                choices = make_options(question)
                empty_choice = [("", _("Option"))]
                choices = empty_choice + choices
                self.fields[field_name] = forms.ChoiceField(choices=choices, label=question.label, widget=SelectPolls)
            elif question.type_field == TypeFieldEnum.NUMBER:
                self.fields[field_name] = forms.IntegerField(label=question.label)
            elif question.type_field == TypeFieldEnum.EMAIL:
                extra_options = {
                    "min_length": question.extra_options.get('minlength') or self.settings_app_validators["min_length"][
                        "email"],
                    "max_length": question.extra_options.get('maxlength') or self.settings_app_validators["max_length"][
                        "email"],
                }
                self.fields[field_name] = forms.EmailField(label=question.label, **extra_options)
                self.fields[field_name].widget.attrs.update(autocomplete="on")
            elif question.type_field == TypeFieldEnum.DATE:
                self.fields[field_name] = forms.DateField(label=question.label,
                                                          widget=forms.DateInput(attrs={'type': 'date'}))
            elif question.type_field == TypeFieldEnum.TEXTAREA:
                extra_options = {
                    "min_length": question.extra_options.get('minlength') or self.settings_app_validators["min_length"][
                        "text_area"],
                    "max_length": question.extra_options.get('maxlength') or self.settings_app_validators["max_length"][
                        "text_area"],
                }
                self.fields[field_name] = forms.CharField(label=question.label, widget=forms.Textarea, **extra_options)

            elif question.type_field == TypeFieldEnum.RATING:
                values = []
                for value in question.options.split('|'):
                    value = value.strip()
                    values.append(value)
                star_default = 1
                if (question.extra_options.get('star_default', None) is not None and
                        question.extra_options.get('star_default') > 0):
                    star_default = int(question.extra_options.pop('star_default'))
                    if star_default > len(values):
                        star_default = int(len(values))
                value_default = values[star_default - 1]
                self.fields[field_name] = forms.IntegerField(label=question.label,
                                                             widget=RatingPolls(
                                                                 attrs={"values": values, "star_default": star_default,
                                                                        "value_default": value_default, }))
            else:
                extra_options = {
                    "min_length": question.extra_options.get('minlength') or self.settings_app_validators["min_length"][
                        "text"],
                    "max_length": question.extra_options.get('maxlength') or self.settings_app_validators["max_length"][
                        "text"],
                }
                self.fields[field_name] = forms.CharField(label=question.label, **extra_options)
            if question.type_field != TypeFieldEnum.RATING:
                self.fields[field_name].widget.attrs.update(question.extra_options)
            if not self.poll.published:
                self.fields[field_name].disabled = True
            self.fields[field_name].required = question.required
            self.fields[field_name].help_text = question.help_text
            self.field_names.append(field_name)

    def clean(self):
        cleaned_data = super().clean()
        if not self.poll.published:
            raise forms.ValidationError(_("The form cannot be saved because the poll is not enabled."),
                                        code="unpublished")
        for field_name in self.field_names:
            try:
                field = cleaned_data[field_name]
            except KeyError:
                raise forms.ValidationError("You must enter valid data")

            if self.fields[field_name].required and not field:
                self.add_error(field_name, 'This field is required')

        return cleaned_data

    @transaction.atomic
    def save(self):
        b_return = False
        try:
            answers = []
            cleaned_data = super().clean()
            user_email = cleaned_data.get("email", None)
            for question in self.questions:
                field_name = f'field_zb_polls_{question.id}'
                if question.type_field == TypeFieldEnum.MULTISELECT:
                    value = "|".join(cleaned_data[field_name])
                else:
                    value = cleaned_data[field_name]
                answer = Answer(question=question, value=value, email=user_email)
                answer.full_clean()
                answer.save()
                answers.append({"question": answer.question.label, "answer": answer.value})
        except forms.ValidationError as e:
            self.add_error(None, e)
        else:
            b_return = True
            if self.poll.notification_to:
                try:
                    email_context = {
                        "poll_title": self.poll.title,
                        "answers": answers,
                        "user_email": user_email,
                    }
                    email = Email(
                        subject=_("Poll responses (%(title)s)") % {"title": self.poll.title},
                        to=self.poll.notification_to
                    )
                    email.set_text_template("djangocms_zb_polls/mail/poll_responses.txt", context=email_context)
                    email.send()
                except (BadHeaderError, ConnectionError) as e:
                    print(e)
                except Exception as exc:
                    print(exc)
        return b_return


class RatingPolls(forms.HiddenInput):
    template_name = "djangocms_zb_polls/widgets/star_rating.html"

class SelectPolls(forms.Select):
    option_template_name = "djangocms_zb_polls/widgets/zb_select_option.html"