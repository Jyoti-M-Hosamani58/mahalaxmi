"""
URL configuration for consign project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from mahalaxmi_app import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    path('',views.userlogin,name='userlogin'),

    path('admin_home/',views.admin_home,name='admin_home'),
    path('company',views.company,name='company'),
    path('viewCompany',views.viewCompany,name='viewCompany'),

    path('users',views.users,name='users'),
    path('viewUser',views.viewUser,name='viewUser'),
    path('editUser/<int:pk>',views.editUser,name='editUser'),
    path('deleteUser/<int:pk>',views.deleteUser,name='deleteUser'),

    path('customer/', views.customer, name='customer'),
    path('viewCustomer',views.viewCustomer,name='viewCustomer'),
    path('editCustomer/<int:customer_id>/', views.editCustomer, name='editCustomer'),
    path('loanHistory/<int:customer_id>/', views.loanHistory, name='loanHistory'),
    path('deleteCustomer/<int:customer_id>/', views.deleteCustomer, name='deleteCustomer'),
    path('deleteLoan/<str:serialNo>/', views.deleteLoan, name='deleteLoan'),

    path('dailyLoanEntry/',views.dailyLoanEntry,name='dailyLoanEntry'),
    path('get_loan_data/<str:serialNo>/', views.get_loan_data, name='get_loan_data'),

    path('loanEntry',views.loanEntry,name='loanEntry'),
    path('get-customer-details_list/<str:serial_no>/', views.get_customer_details_list, name='get_customer_details_list'),

    path('index',views.index,name='index'),
    path('get_loan_tabledata/', views.get_loan_tabledata, name='get_loan_tabledata'),
    path('update_loan/', views.update_loan, name='update_loan'),

    path('daily_loan_count_page/', views.daily_loan_count_page, name='daily_loan_count_page'),
    path('gold_loan_count_page/', views.gold_loan_count_page, name='gold_loan_count_page'),
    path('vehicle_loan_count_page/', views.vehicle_loan_count_page, name='vehicle_loan_count_page'),
    path('monthly_loan_count_page/', views.monthly_loan_count_page, name='monthly_loan_count_page'),
    path('property_loan_count_page/', views.property_loan_count_page, name='property_loan_count_page'),
    path('loan_pending_count_page/', views.loan_pending_count_page, name='loan_pending_count_page'),
    path('get_missing_daily_loan_details/', views.get_missing_daily_loan_details, name='get_missing_daily_loan_details'),
    path('customers_without_dailyloan_today_view/', views.customers_without_dailyloan_today_view, name='customers_without_dailyloan_today_view'),
    path('loan_completed/', views.loan_completed, name='loan_completed'),
    path('get_customer_name/', views.get_customer_name, name='get_customer_name'),
    path('get_customer_details/', views.get_customer_details, name='get_customer_details'),

    path('recoveryReport',views.recoveryReport,name='recoveryReport'),
    path('loanRecoveryReport',views.loanRecoveryReport,name='loanRecoveryReport'),
    path('loanPrincipleRecoveryReport',views.loanPrincipleRecoveryReport,name='loanPrincipleRecoveryReport'),
    path('outgoingReport',views.outgoingReport,name='outgoingReport'),

    path('add-loan/<int:customer_id>/',views.add_loan, name='add_loan'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



