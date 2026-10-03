import re

from django import forms


class TechStackRadioGroups(forms.SelectMultiple):
    """One radio group per selected stack; the form still validates a queryset."""

    template_name = "website/widgets/tech_stack_radios.html"

    def value_from_datadict(self, data, files, name):
        group_names = [key for key in data if re.fullmatch(rf"{re.escape(name)}_\d+", key)]
        if group_names:
            return [data[key] for key in group_names]
        return super().value_from_datadict(data, files, name)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        widget = context["widget"]
        selected = widget["value"] or [""]
        choices = [(str(value), label) for value, label in self.choices]
        widget["groups"] = [
            {
                "index": index,
                "options": [
                    {"value": value, "label": label, "checked": value == str(selection)}
                    for value, label in choices
                ],
            }
            for index, selection in enumerate(selected)
        ]
        return context
