from django import forms
from django.contrib.auth.forms import UserCreationForm    
#from django.contrib.auth.models import Group
#from .models import CustomGroup
from .models import Group

class CustomUserCreationForm(UserCreationForm):  # On Utilise les formulaires générées par la class UserCreation de Django qu'on personnalise
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("password1", "password2")

class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']