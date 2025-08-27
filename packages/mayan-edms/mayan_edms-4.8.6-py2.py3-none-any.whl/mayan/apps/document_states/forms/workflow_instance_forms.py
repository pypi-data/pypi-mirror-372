from django.utils.translation import gettext_lazy as _

from mayan.apps.forms import form_fields, forms

from ..models import WorkflowTransition


class WorkflowInstanceTransitionSelectForm(forms.Form):
    def __init__(self, user, workflow_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[
            'transition'
        ].queryset = workflow_instance.get_transition_choices(user=user)

    transition = form_fields.ModelChoiceField(
        help_text=_(
            message='Select a transition to execute in the next step.'
        ), label=_(message='Transition'),
        queryset=WorkflowTransition.objects.none()
    )
