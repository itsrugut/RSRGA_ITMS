from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class CustomUserCreationForm(UserCreationForm):
    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")

        # Check for minimum length
        if len(password1) < 8:
            raise ValidationError("Password must be at least 8 characters long.")

        # Check for at least one uppercase letter
        if not any(char.isupper() for char in password1):
            raise ValidationError("Password must contain at least one uppercase letter.")

        # Check for at least one lowercase letter
        if not any(char.islower() for char in password1):
            raise ValidationError("Password must contain at least one lowercase letter.")

        # Check for at least one digit
        if not any(char.isdigit() for char in password1):
            raise ValidationError("Password must contain at least one digit.")

        # Check for at least one special character
        special_characters = "!@#$%^&*()-+?_=,<>/"
        if not any(char in special_characters for char in password1):
            raise ValidationError("Password must contain at least one special character (!@#$%^&*()-+?_=,<>/)")

        return password1

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")