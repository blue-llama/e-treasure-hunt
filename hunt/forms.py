from django import forms
from django.forms import formset_factory
from hunt.models import Level, Answer
from hunt.validators import validate_answer_file, validate_all_hints_provided


class LevelForm(forms.Form):
    number = forms.IntegerField(label="Number")
    clue = forms.ImageField(widget=forms.FileInput, required=False)
    hints = forms.ImageField(
        widget=forms.FileInput(attrs={"multiple": True}),
        #validators=[validate_all_hints_provided],
        required=False
    )
    answered_by = forms.ModelMultipleChoiceField(
        queryset=Answer.objects.all().values_list('name', flat=True), required=False
    )


class AnswerForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100)
    description = forms.FileField(widget=forms.FileInput)
    info = forms.FileField(widget=forms.FileInput, validators=[validate_answer_file])


AnswerFormSet = formset_factory(AnswerForm, extra=1)
