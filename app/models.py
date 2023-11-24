from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class AccountsTable(models.Model):

    method = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    amount_method = (
        ('bank', 'Bank'),
        ('cash', 'Cash'),
        ('savings', 'Savings')
    )

    income_category = (
        ('salary', 'Salary'),
        ('loan', 'Loan'),
        ('other', 'Others'),
    )

    expense_category = (
        ('food', 'Food'),
        ('transport', 'Transport'),
        ('rent', 'Rent'),
        ('shopping', 'Shopping'),
        ('snacks', 'Snacks'),
        ('medical', 'Medical'),
        ('telephone', 'Telephone'),
        ('entertainment', 'Entertainment'),
        ('bill', 'Bills'),
        ('education', 'Education'),
        ('social', 'Social'),
        ('loan', 'Loan'),
        ('other', 'Other'),
    )

    # category_choices = income_category + expense_category

    id = models.IntegerField(primary_key=True, editable=False)
    amount = models.IntegerField(blank=True, null=True)
    remark = models.CharField(max_length=200, null=True, blank=True, default='')
    status = models.CharField(max_length=200,choices=method)
    created_by = models.DateTimeField(auto_now_add=True)
    updated_by = models.DateTimeField(auto_now=True)
    amount_status = models.CharField(max_length=200, choices=amount_method)
    category = models.CharField(max_length=200, choices=income_category)
    categorys = models.CharField(max_length=200, choices=expense_category)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.remark} | {self.amount}"