from django import forms
from django.forms import formset_factory
from hunt.models import Level, Answer
from hunt.validators import (
    validate_answer_file,
    validate_answer_name,
)


class LevelUploadForm(forms.Form):
    number = forms.IntegerField(label="Number")
    clue = forms.ImageField(widget=forms.FileInput)
    hint1 = forms.ImageField(label="Hint 1", widget=forms.FileInput)
    hint2 = forms.ImageField(label="Hint 2", widget=forms.FileInput)
    hint3 = forms.ImageField(label="Hint 3", widget=forms.FileInput)
    hint4 = forms.ImageField(label="Hint 4", widget=forms.FileInput)
    answered_by = forms.ModelMultipleChoiceField(
        queryset=Answer.objects.all().values_list("name", flat=True), required=False
    )


class AnswerUploadForm(forms.Form):
    name = forms.CharField(
        label="Name", max_length=100, validators=[validate_answer_name]
    )
    description = forms.FileField(widget=forms.FileInput)
    info = forms.FileField(widget=forms.FileInput, validators=[validate_answer_file])


AnswerUploadFormSet = formset_factory(AnswerUploadForm, extra=1)
