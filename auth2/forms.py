from django import forms
from django.contrib.auth.forms import UserCreationForm

from auth2.models import User


class Auth2UserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Телеграм чат ID'
        password = User.objects.make_random_password(length=30)
        self.fields['password1'].widget = forms.HiddenInput()
        self.fields['password1'].initial = password
        self.fields['password2'].widget = forms.HiddenInput()
        self.fields['password2'].initial = password

    class Meta:
        model = User
        fields = ('tg_chat_id',)
