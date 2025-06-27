from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.root_redirect_view, name='root'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('bank/<int:id>/', views.view_bank, name='view_bank'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('deposit/', views.deposit_view, name='deposit'),
    path('withdraw/', views.withdraw_view, name='withdraw'),
    path('transfer/', views.transfer_view, name='transfer'),
    path('admin-only/', views.admin_only_view, name='admin_only'),
    path('create-account/', views.create_account_view, name='create_account'),
    path('account-info/', views.account_info_view, name='account_info'),
] 