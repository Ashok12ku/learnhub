from django import forms
from django.forms import inlineformset_factory
from .models import Course, Category, Section, Lesson


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "category", "description", "thumbnail", "course_type", "price"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Python for Beginners"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "thumbnail": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "course_type": forms.Select(attrs={"class": "form-select", "id": "id_course_type"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "id": "id_price"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["price"].required = False
        self.fields["category"].required = False
        if Category.objects.count() == 0:
            self.fields["category"].empty_label = "No categories yet (ask Admin to add one)"


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["title", "order"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Section 1: Introduction"}),
            "order": forms.NumberInput(attrs={"class": "form-control", "style": "width:90px"}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "lesson_type", "video_file", "video_url", "pdf_file", "order", "is_preview"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Lesson title"}),
            "lesson_type": forms.Select(attrs={"class": "form-select"}),
            "video_file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "video_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://... (optional)"}),
            "pdf_file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control", "style": "width:90px"}),
            "is_preview": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Web Development"})}
