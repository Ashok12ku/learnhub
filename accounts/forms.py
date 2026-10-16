from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


def add_bootstrap_widget_classes(form):
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            css_class = "form-check-input"
        elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
            css_class = "form-select"
        else:
            css_class = "form-control"

        classes = widget.attrs.get("class", "").split()
        if css_class not in classes:
            classes.append(css_class)
        widget.attrs["class"] = " ".join(classes)


class StudentSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False, max_length=15)

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_widget_classes(self)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data.get("phone")
        user.is_approved = True  # students don't need approval
        if commit:
            user.save()
        return user


class TeacherSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False, max_length=15)
    expertise = forms.CharField(required=False, max_length=255)
    qualification = forms.CharField(required=False, max_length=255)

    class Meta:
        model = User
        fields = ["username", "email", "phone", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_widget_classes(self)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.TEACHER
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data.get("phone")
        user.is_approved = False  # needs Admin approval before creating courses
        if commit:
            user.save()
            from .models import TeacherProfile
            TeacherProfile.objects.create(
                user=user,
                expertise=self.cleaned_data.get("expertise", ""),
                qualification=self.cleaned_data.get("qualification", ""),
            )
        return user


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "bio", "profile_picture"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap_widget_classes(self)
