from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import BankAccount

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)

class WithdrawForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)

class TransferForm(forms.Form):
    recipient_account_number = forms.CharField(max_length=12)
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)

class BankAccountCreateForm(forms.ModelForm):
    initial_deposit = forms.DecimalField(
        max_digits=12, decimal_places=2, min_value=0, required=False, label="Initial Deposit", initial=0
    )
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.TextInput())
    class Meta:
        model = BankAccount
        fields = ['first_name', 'last_name', 'date_of_birth', 'address', 'phone_number'] 