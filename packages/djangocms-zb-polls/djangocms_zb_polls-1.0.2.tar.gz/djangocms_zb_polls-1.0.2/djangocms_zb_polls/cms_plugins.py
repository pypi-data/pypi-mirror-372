#  Developed by CQ Inversiones SAS. Copyright ©. 2019-2025. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019-2025. Todos los derechos reservados.

# ****************************************************************
# IDE:          PyCharm
# Developed by: "Jhony Alexander Gonzalez Cordoba"
# Date:         13/08/2025 - 3:42 p. m.
# Project:      cms_plugins
# Module Name:  cms_plugins
# Description: 
# ****************************************************************
import os
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from djangocms_zb_polls.forms import PollForm
from djangocms_zb_polls.models import PluginConfig


@plugin_pool.register_plugin
class DjangoCMSZBPollsPlugin(CMSPluginBase):
    name = _("Zibanu Polls Extension")
    module = "Zibanu"
    cache = False
    model = PluginConfig
    autocomplete_fields = ["poll"]

    def _get_render_template(self, context, instance, placeholder):
        """
        Private method to replace default template in CMS
        :param context: Context CMS Var
        :param instance: Model instance
        :param placeholder: Placeholder
        :return: str: Name of new template
        """
        base_dir = f"djangocms_zb_polls/plugins/default/"
        base_template = "plugin.html"
        if instance.template:
            base_dir = f"djangocms_zb_polls/plugins/{instance.template}/"

        return os.path.join(base_dir, base_template)

    def get_render_template(self, context, instance, placeholder):
        return self._get_render_template(context, instance, placeholder)

    def render(self, context, instance, placeholder):
        """
        Override method to render template
        :param context: Context CMS Var
        :param instance: Model instance
        :param placeholder: Placeholder
        :return: context
        """
        form = PollForm(poll=instance.poll)
        if context['request'].method == 'POST':
            form = PollForm(poll=instance.poll, data=context['request'].POST)
            if form.is_valid():
                save = form.save()
                if save:
                    messages.success(context["request"], _("¡The form has been saved successfully!"))
                    form = PollForm(poll=instance.poll)
            if form.errors:
                if form.errors.get("__all__", None) is not None:
                    errors = form.errors["__all__"].data
                    for error in errors:
                        if error.code == "unpublished":
                            messages.error(context["request"], str(error.message))
                            form = PollForm(poll=instance.poll)
        context = super().render(context, instance, placeholder)
        context.update({
            "form": form,
        })
        return context
