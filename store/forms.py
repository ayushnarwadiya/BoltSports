from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Order

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'address', 'city', 'pincode']
        widgets = {'address': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if not (phone.isdigit() and len(phone) == 10):
            raise forms.ValidationError('Enter a valid 10-digit mobile number.')
        return phone

    def clean_pincode(self):
        pincode = self.cleaned_data['pincode'].strip()
        if not (pincode.isdigit() and len(pincode) == 6):
            raise forms.ValidationError('Enter a valid 6-digit pincode.')
        return pincode
