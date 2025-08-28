from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class RegistrationForm(UserCreationForm): #email verplicht hier
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email")

class EmailOrUsernameAuthenticationForm(forms.Form): #username of email dus handiger (flexibler) #TODO apart user en email mapping doen
    login = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned = super().clean()
        login = cleaned.get("login")
        password = cleaned.get("password")
        user = authenticate(username=login, password=password)
        if user is None:
            try:
                email_user = User.objects.get(email__iexact=login)
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid credentials")
            user = authenticate(username=email_user.get_username(), password=password)
            if user is None:
                raise forms.ValidationError("Invalid credentials")
        cleaned["user"] = user
        return cleaned
