from django import forms
from .models import Test, Question


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = [
            "title", "duration_minutes", "pass_percentage",
            "negative_marking", "negative_marks_per_wrong",
            "attempt_limit", "randomize_questions",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Python Basics Test"}),
            "duration_minutes": forms.NumberInput(attrs={"class": "form-control"}),
            "pass_percentage": forms.NumberInput(attrs={"class": "form-control"}),
            "negative_marking": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "negative_marks_per_wrong": forms.NumberInput(attrs={"class": "form-control", "step": "0.25"}),
            "attempt_limit": forms.NumberInput(attrs={"class": "form-control"}),
            "randomize_questions": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["question_text", "option_a", "option_b", "option_c", "option_d", "correct_option", "order"]
        widgets = {
            "question_text": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Question text"}),
            "option_a": forms.TextInput(attrs={"class": "form-control", "placeholder": "Option A"}),
            "option_b": forms.TextInput(attrs={"class": "form-control", "placeholder": "Option B"}),
            "option_c": forms.TextInput(attrs={"class": "form-control", "placeholder": "Option C"}),
            "option_d": forms.TextInput(attrs={"class": "form-control", "placeholder": "Option D"}),
            "correct_option": forms.Select(attrs={"class": "form-select"}),
            "order": forms.NumberInput(attrs={"class": "form-control", "style": "width:90px"}),
        }
