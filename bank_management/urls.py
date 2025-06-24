"""
URL configuration for bank_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('bank/<int:id>/', view_bank, name='view_bank'),
]
