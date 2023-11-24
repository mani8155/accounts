from django.urls import path
from . import views

urlpatterns = [
   path('', views.accounts, name="accounts"),
   path('create/', views.add_accounts, name="add-account"),
   path('edit/<int:pk>/', views.edit_accounts, name="edit-account"),
   path('delete/<int:pk>/', views.delete_accounts, name="delete-account"),
   path('ac_page/', views.account_page, name="ac-page"),

   path('income_data/', views.income_data, name="income-data"),
   path('income_edit_data/<int:pk>/', views.edit_income_accounts, name="income-edit-data"),
   path('income_delete_data/<int:pk>/', views.income_delete_accounts, name="income-delete-data"),

   path('expense_data/', views.expense_data, name="expense-data"),
   path('expense_edit_data/<int:pk>/', views.edit_expense_accounts, name="expense-edit-data"),
   path('expense_delete_data/<int:pk>/', views.expense_delete_accounts, name="expense-delete-data"),
   path('expense_filter/', views.expense_filter, name="expense-filter"),

   path('income_filter/', views.income_filter, name="income-filter"),

   path('download/', views.all_data_download, name='download'),
   path('income_download/', views.income_data_download, name='income-download'),
   path('expense_download/', views.expense_data_download, name='expense-download'),

   path('month_income/<int:month>/<int:year>/', views.income_month_download, name="month-income"),
   path('date_range_income/<str:start_date>/<str:end_date>/', views.date_range_income_download, name="date_range-income"),
   path('date_range_income/<str:date_field>/', views.income_date_filter_download, name="date-income-download"),

   path('month_expense/<int:month>/<int:year>/', views.expense_month_download, name="month-expense"),
   path('date_range_expense/<str:start_date>/<str:end_date>/', views.date_range_expense_download,
        name="date_range-expense"),
   path('date_range_expense/<str:date_field>/', views.expense_date_filter_download, name="date-expense-download"),


   path('savings/', views.savings_amount, name="savings"),
   path('savings_pdf/', views.savings_data_download, name="savings-pdf"),


]
