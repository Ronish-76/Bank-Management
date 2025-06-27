from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from .models import BankAccount, Transaction

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_number', 'balance', 'is_active']
    list_filter = ['is_active', 'user']
    search_fields = ['account_number', 'user__username']
    actions = ['enable_accounts', 'disable_accounts']
    list_editable = ['balance', 'is_active']

    def enable_accounts(self, request, queryset):
        queryset.update(is_active=True)
    enable_accounts.short_description = "Enable selected accounts"

    def disable_accounts(self, request, queryset):
        queryset.update(is_active=False)
    disable_accounts.short_description = "Disable selected accounts"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('transaction-report/', self.admin_site.admin_view(self.transaction_report), name='transaction-report'),
        ]
        return custom_urls + urls

    def transaction_report(self, request):
        transactions = Transaction.objects.all().order_by('-timestamp')
        context = dict(
            self.admin_site.each_context(request),
            transactions=transactions,
        )
        return TemplateResponse(request, "admin/transaction_report.html", context)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'type', 'amount', 'timestamp']
    list_filter = ['type', 'timestamp', 'account']
    search_fields = ['account__account_number', 'account__user__username']
