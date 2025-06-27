from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import RegisterForm, DepositForm, WithdrawForm, TransferForm, BankAccountCreateForm
from django.contrib.auth.decorators import login_required
from .models import BankAccount, Transaction
from django.db import transaction as db_transaction
from django.http import HttpResponseForbidden
import random
import base64

banks = []
next_id = 1

def home(request):
    global banks, next_id
    if request.method == 'POST':
        if 'bank_name' in request.POST:
            name = request.POST['bank_name']
            banks.append({'id': next_id, 'bank_name': name, 'balance': 0})
            next_id += 1
            messages.success(request, 'Bank added successfully!')
        elif 'amount' in request.POST:
            index = int(request.POST['bank_index'])
            amount = int(request.POST['amount'])
            if 'add_balance' in request.POST:
                banks[index]['balance'] += amount
                messages.success(request, 'Balance added successfully!')
            elif 'remove_balance' in request.POST:
                if banks[index]['balance'] >= amount:
                    banks[index]['balance'] -= amount
                    messages.success(request, 'Balance removed successfully!')
                else:
                    messages.error(request, 'Insufficient balance!')
        elif 'delete_bank' in request.POST:
            index = int(request.POST['bank_index'])
            banks.pop(index)
            messages.success(request, 'Bank deleted successfully!')
        return redirect('home')
    return render(request, 'home.html', {'banks': banks})

def view_bank(request, id):
    global banks
    bank = next((b for b in banks if str(b['id']) == str(id)), None)
    if not bank:
        messages.error(request, 'Bank not found!')
        return redirect('home')
    return render(request, 'bank_detail.html', {'bank': bank})

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "core/register.html", {"form": form})

@login_required
def dashboard_view(request):
    account = BankAccount.objects.filter(user=request.user).first()
    transactions = Transaction.objects.filter(account=account).order_by('-timestamp') if account else []
    decoded_number = account.account_number if account else None
    if not account and request.method == 'POST':
        # Generate a unique 12-digit account number
        while True:
            account_number = str(random.randint(100000000000, 999999999999))
            if not BankAccount.objects.filter(account_number=account_number).exists():
                break
        BankAccount.objects.create(user=request.user, account_number=account_number)
        messages.success(request, 'Bank account created!')
        return redirect('dashboard')
    return render(request, 'core/dashboard.html', {
        'account': account,
        'transactions': transactions,
        'decoded_number': decoded_number,
    })

@login_required
def deposit_view(request):
    account = BankAccount.objects.filter(user=request.user).first()
    if not account:
        messages.error(request, "No account found.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            with db_transaction.atomic():
                account.balance += amount
                account.save()
                Transaction.objects.create(account=account, type='deposit', amount=amount, description='Deposit')
            messages.success(request, f"Deposited ₹{amount} successfully.")
            return redirect('dashboard')
    else:
        form = DepositForm()
    return render(request, 'core/deposit.html', {'form': form, 'account': account})

@login_required
def withdraw_view(request):
    account = BankAccount.objects.filter(user=request.user).first()
    if not account:
        messages.error(request, "No account found.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = WithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if account.balance < amount:
                messages.error(request, "Insufficient balance.")
            else:
                with db_transaction.atomic():
                    account.balance -= amount
                    account.save()
                    Transaction.objects.create(account=account, type='withdrawal', amount=amount, description='Withdrawal')
                messages.success(request, f"Withdrew ₹{amount} successfully.")
                return redirect('dashboard')
    else:
        form = WithdrawForm()
    return render(request, 'core/withdraw.html', {'form': form, 'account': account})

@login_required
def transfer_view(request):
    account = BankAccount.objects.filter(user=request.user).first()
    if not account:
        messages.error(request, "No account found.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            recipient_number = form.cleaned_data['recipient_account_number']
            amount = form.cleaned_data['amount']
            if account.account_number == recipient_number:
                messages.error(request, "Cannot transfer to your own account.")
            elif account.balance < amount:
                messages.error(request, "Insufficient balance.")
            else:
                recipient = BankAccount.objects.filter(account_number=recipient_number, is_active=True).first()
                if not recipient:
                    messages.error(request, "Recipient account not found or inactive.")
                else:
                    with db_transaction.atomic():
                        account.balance -= amount
                        recipient.balance += amount
                        account.save()
                        recipient.save()
                        Transaction.objects.create(account=account, type='transfer', amount=amount, description=f'Transfer to {recipient_number}')
                        Transaction.objects.create(account=recipient, type='deposit', amount=amount, description=f'Transfer from {account.account_number}')
                    messages.success(request, f"Transferred ₹{amount} to {recipient_number} successfully.")
                    return redirect('dashboard')
    else:
        form = TransferForm()
    return render(request, 'core/transfer.html', {'form': form, 'account': account})

def generate_next_account_number():
    last_account = BankAccount.objects.order_by('-id').first()
    if last_account:
        try:
            last_number = int(last_account.account_number)
        except Exception:
            last_number = 99
        next_number = last_number + 1
    else:
        next_number = 100
    return str(next_number)

@login_required
def create_account_view(request):
    if BankAccount.objects.filter(user=request.user).exists():
        return redirect('dashboard')
    if request.method == 'POST':
        form = BankAccountCreateForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            raw_number = generate_next_account_number()
            account.account_number = raw_number
            account.user = request.user
            account.save()
            initial_deposit = form.cleaned_data.get('initial_deposit')
            if initial_deposit and initial_deposit > 0:
                account.balance = initial_deposit
                account.save()
            messages.success(request, 'Bank account created!')
            return redirect('dashboard')
    else:
        form = BankAccountCreateForm()
    return render(request, 'core/create_account.html', {'form': form})

# Example of a custom admin-only view
def admin_only_view(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("You do not have permission to access this page.")
    # Admin logic here
    return render(request, 'core/admin_only.html')

def root_redirect_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return redirect('dashboard')

@login_required
def account_info_view(request):
    account = BankAccount.objects.filter(user=request.user).first()
    decoded_number = account.account_number if account else None
    return render(request, 'core/account_info.html', {'account': account, 'decoded_number': decoded_number})
