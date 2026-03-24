from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email"]


class ProfileUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(
        required=False,
        input_formats=["%d.%m.%Y"],
        widget=forms.DateInput(
            format="%d.%m.%Y",
            attrs={"placeholder": "ДД.ММ.ГГГГ"},
        ),
    )

    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "+7 921 978 42 23"}),
        validators=[
            RegexValidator(
                regex=r"^\+7 \d{3} \d{3} \d{2} \d{2}$",
                message="Телефон должен быть в формате: +7 921 978 42 23",
            )
        ],
    )

    class Meta:
        model = Profile
        fields = ["full_name", "birth_date", "position", "phone", "image"]

    def clean_phone(self):
        value = self.cleaned_data.get("phone", "") or ""
        # Normalize various user inputs to +7 XXX XXX XX XX when possible
        digits = "".join(ch for ch in value if ch.isdigit())
        if not digits:
            return ""

        if digits.startswith("8") and len(digits) == 11:
            digits = "7" + digits[1:]
        if digits.startswith("7") and len(digits) == 11:
            return f"+7 {digits[1:4]} {digits[4:7]} {digits[7:9]} {digits[9:11]}"

        return value.strip()