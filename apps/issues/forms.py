from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Issue


class IssueForm(forms.ModelForm):

    class Meta:

        model = Issue

        fields = [
            "title",
            "description",
            "category",
            "location",
            "latitude",
            "longitude",
            "image",
        ]

        widgets = {

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _(
                        "e.g. Large pothole near main road"
                    ),
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": _(
                        "Describe the issue clearly..."
                    ),
                    "rows": 5,
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _(
                        "Select a location on the map"
                    ),
                    "readonly": "readonly",
                }
            ),

            "latitude": forms.HiddenInput(),

            "longitude": forms.HiddenInput(),

            "image": forms.ClearableFileInput(
                attrs={
                    "class": "evidence-file-input form-control",
                    "accept": "image/*",
                }
            ),
        }

    def clean_title(self):

        title = self.cleaned_data["title"]

        if len(title.strip()) < 5:

            raise forms.ValidationError(
                _(
                    "Title must contain at least 5 characters."
                )
            )

        return title.strip()

    def clean_description(self):

        description = self.cleaned_data["description"]

        if len(description.strip()) < 15:

            raise forms.ValidationError(
                _(
                    "Please provide a little more information "
                    "about the issue."
                )
            )

        return description.strip()

    def clean_location(self):

        location = self.cleaned_data["location"]

        if not location or len(location.strip()) < 3:

            raise forms.ValidationError(
                _(
                    "Please select a valid location on the map."
                )
            )

        return location.strip()

    def clean_latitude(self):

        latitude = self.cleaned_data.get("latitude")

        if latitude is None:

            raise forms.ValidationError(
                _(
                    "Please select the issue location on the map."
                )
            )

        return latitude

    def clean_longitude(self):

        longitude = self.cleaned_data.get("longitude")

        if longitude is None:

            raise forms.ValidationError(
                _(
                    "Please select the issue location on the map."
                )
            )

        return longitude