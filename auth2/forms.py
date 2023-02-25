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


class FreelancerUserChangeForm(UserChangeForm):
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

    def clean_is_active(self):
        is_active = self.cleaned_data["is_active"]
        payrate = self.data["freelancerprofile-0-payrate"]
        if is_active and not payrate:
            raise ValidationError("Вы не можете активировать фрилансера не назначив ему оклад")
        return is_active
