from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from auth2.models import User, Freelancer


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


class TelegramUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Freelancer
        fields = (
            'tg_chat_id',
            'password',
            'first_name',
            'last_name',
            'is_active',
        )
    def clean_is_staff(self):
        is_staff = self.cleaned_data["is_staff"]
        if is_staff:
            raise ValidationError("Вы не можете дать обычному пользователю доступ в админку")
        return is_staff

    def clean_is_superuser(self):
        is_superuser = self.cleaned_data["is_superuser"]
        if is_superuser:
            raise ValidationError("Вы не можете сделать обычного пользователя суперюзером")
        return is_superuser
