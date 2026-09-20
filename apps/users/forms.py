from django import forms
from django.utils.translation import gettext_lazy as _

from .models import User


# =============================================================
# CITIZEN REGISTRATION FORM
# =============================================================

class CitizenRegistrationForm(forms.ModelForm):

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter password"),
            }
        ),
    )

    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Confirm password"),
            }
        ),
    )

    # ---------------------------------------------------------
    # GOVERNMENT ACCESS REQUEST
    # ---------------------------------------------------------

    request_government_role = forms.BooleanField(
        required=False,
        label=_("Request Government Official Access"),
        help_text=_(
            "Your account will remain a citizen account "
            "until an administrator approves your request."
        ),
    )

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
        ]

        widgets = {

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter first name"),
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter last name"),
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter email address"),
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter phone number"),
                }
            ),
        }

    # ---------------------------------------------------------
    # EMAIL VALIDATION
    # ---------------------------------------------------------

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                _("An account with this email already exists.")
            )

        return email

    # ---------------------------------------------------------
    # PASSWORD VALIDATION
    # ---------------------------------------------------------

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                _("Passwords do not match.")
            )

        return cleaned_data


# =============================================================
# CITIZEN PROFILE FORM
# =============================================================

class CitizenProfileForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "profile_image",
            "preferred_language",
        ]

        labels = {
            "first_name": _("First Name"),
            "last_name": _("Last Name"),
            "phone_number": _("Phone Number"),
            "profile_image": _("Profile Photo"),
            "preferred_language": _("Language Preference"),
        }

        widgets = {

            "first_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter your first name"),
                    "autocomplete": "given-name",
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter your last name"),
                    "autocomplete": "family-name",
                }
            ),

            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Enter your phone number"),
                    "autocomplete": "tel",
                    "inputmode": "tel",
                }
            ),

            "profile_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),

            "preferred_language": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
        }

    # ---------------------------------------------------------
    # PHONE NUMBER VALIDATION
    # ---------------------------------------------------------

    def clean_phone_number(self):
        phone = self.cleaned_data.get(
            "phone_number",
            ""
        ).strip()

        if phone and not phone.replace("+", "").isdigit():
            raise forms.ValidationError(
                _("Please enter a valid phone number.")
            )

        return phone