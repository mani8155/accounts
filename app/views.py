from datetime import timedelta, datetime

from django.shortcuts import render, redirect
from .models import AccountsTable
from .forms import CreateAccountsForm, ACForm, ACDateForm, MonthForm
from django.db.models import Q, Sum

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required
def accounts(request):
    obj = AccountsTable.objects.filter(user=request.user).order_by('-updated_by')[:7]
    context = {"ac_table_data": obj, "menu": "menu-records"}
    return render(request, 'home.html', context)


@login_required
def add_accounts(request):
    form = CreateAccountsForm()

    if request.method == 'POST':
        form = CreateAccountsForm(request.POST)

        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user  # Associate the account with the current user
            account.save()
            return redirect('accounts')

    context = {"form": form, "menu": "menu-records"}
    return render(request, 'accounts_form.html', context)


@login_required
def edit_accounts(request, pk):
    account = AccountsTable.objects.get(user=request.user, id=pk)
    form = CreateAccountsForm(instance=account)

    if request.method == "POST":
        form = CreateAccountsForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect('accounts')

    context = {'form': form, "menu": "menu-records"}
    return render(request, 'accounts_form.html', context)


@login_required
def delete_accounts(request, pk):
    account = AccountsTable.objects.get(user=request.user, id=pk)
    if request.method == 'POST':
        account.delete()
        return redirect('accounts')

    context = {"obj": account, "menu": "menu-records"}
    return render(request, 'deleteACform.html', context)


@login_required
def account_page(request):
    income_bank_data = AccountsTable.objects.filter(user=request.user, status='income', amount_status='bank')

    if income_bank_data.exists():
        bank_income_amount = income_bank_data.aggregate(bank_income_amount=Sum('amount'))['bank_income_amount']
    else:
        bank_income_amount = 0

    expense_baml_data = AccountsTable.objects.filter(user=request.user, status='expense', amount_status='bank')
    bank_expense_amount = expense_baml_data.aggregate(bank_expense_amount=Sum('amount'))['bank_expense_amount'] or 0

    bank = bank_income_amount - bank_expense_amount

    # -------------------- ---------------- -------------------

    income_cash_data = AccountsTable.objects.filter(user=request.user, status='income', amount_status='cash')
    cash_income_amount = income_cash_data.aggregate(cash_income_amount=Sum('amount'))['cash_income_amount'] or 0

    expense_cash_data = AccountsTable.objects.filter(user=request.user, status='expense', amount_status='cash')
    cash_expense_amount = expense_cash_data.aggregate(cash_expense_amount=Sum('amount'))['cash_expense_amount'] or 0

    cash = cash_income_amount - cash_expense_amount
    context = {"menu": "menu-acPage", "bank_total_amount": bank, "cash_total_amount": cash}

    return render(request, 'account/ac_page.html', context)


# ------------------------------- income -------------------------------------------------
@login_required
def income_data(request):
    data = AccountsTable.objects.filter(user=request.user, status='income').order_by('-updated_by')
    context = {"menu": "menu-income", "income_data": data}
    return render(request, 'income/income_data.html', context)


@login_required
def edit_income_accounts(request, pk):
    account = AccountsTable.objects.get(user=request.user, id=pk)
    form = CreateAccountsForm(instance=account)

    if request.method == "POST":
        form = CreateAccountsForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect('income-data')

    context = {'form': form, "menu": "menu-income"}
    return render(request, 'accounts_form.html', context)


@login_required
def income_delete_accounts(request, pk):
    account = AccountsTable.objects.get(user=request.user, id=pk)
    if request.method == 'POST':
        account.delete()
        return redirect('income-data')

    context = {"obj": account, "menu": "menu-income"}
    return render(request, 'income/delete.html', context)


# ---------------------------- expense ------------------------------------------
@login_required
def expense_data(request):
    data = AccountsTable.objects.filter(user=request.user, status='expense').order_by('-updated_by')
    context = {"menu": "menu-expense", "expense_data": data}
    return render(request, 'expense/expense_data.html', context)


@login_required
def expense_filter(request):
    form = ACForm()
    form2 = ACDateForm()
    month_form = MonthForm()

    if request.method == "POST":

        form_request = request.POST.get('form_request')
        if form_request == 'form1':
            form = ACForm(request.POST)
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                end_date = end_date + timedelta(days=1)

                my_objects = AccountsTable.objects.filter(user=request.user, created_by__range=(start_date, end_date),
                                                          status='expense')

                total_amount = 0
                for obj in my_objects:
                    total_amount += obj.amount

                # print("Total Amount:", total_amount)
                # print(my_objects)
                context = {"menu": "menu-expense", "expense_data": my_objects, "total_amount": total_amount,
                           "start_date": start_date, "end_date": end_date}
                return render(request, 'expense/date_filter.html', context)

        elif form_request == 'form2':
            form2 = ACDateForm(request.POST)
            if form2.is_valid():
                date_field = form2.cleaned_data['date_field']
                date_objects = AccountsTable.objects.filter(user=request.user, created_by__date=date_field,
                                                            status="expense")

                total_amount = 0
                for obj in date_objects:
                    total_amount += obj.amount
                # print(date_objects)
                context = {"menu": "menu-expense", "expense_data": date_objects, "total_amount": total_amount,
                           "date_field": date_field}
                return render(request, 'expense/day_filter.html', context)

        else:
            month_form = MonthForm(request.POST)
            if month_form.is_valid():
                month = month_form.cleaned_data['month_field']
                year = month_form.cleaned_data['year']
                # print(month)
                # print(year)
                month_objects = AccountsTable.objects.filter(
                    Q(created_by__month=month) & Q(created_by__year=year), status="expense", user=request.user
                )
                # print(month_objects)
                total_amount = 0
                for obj in month_objects:
                    total_amount += obj.amount

                context = {"menu": "menu-expense", "expense_data": month_objects,
                           "total_amount": total_amount,
                           "month": month, "year": year
                           }

                return render(request, 'expense/month_filter.html', context)

    context = {"menu": "menu-expense", "form": form, "form2": form2, "month_form": month_form}
    return render(request, 'expense/filter.html', context)


@login_required
def edit_expense_accounts(request, pk):
    account = AccountsTable.objects.get(user=request.user, id=pk)
    form = CreateAccountsForm(instance=account)

    if request.method == "POST":
        form = CreateAccountsForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return redirect('expense-data')

    context = {'form': form, "menu": "menu-expense"}
    return render(request, 'accounts_form.html', context)


@login_required
def expense_delete_accounts(request, pk):
    account = AccountsTable.objects.get(user=request.user, id=pk)
    if request.method == 'POST':
        account.delete()
        return redirect('expense-data')

    context = {"obj": account, "menu": "menu-expense"}
    return render(request, 'expense/delete.html', context)


# --------------------------------------

@login_required
def income_filter(request):
    form = ACForm()
    form2 = ACDateForm()
    month_form = MonthForm()

    if request.method == "POST":

        form_request = request.POST.get('form_request')
        if form_request == 'form1':
            form = ACForm(request.POST)
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                end_date = end_date + timedelta(days=1)

                my_objects = AccountsTable.objects.filter(user=request.user, created_by__range=(start_date, end_date),
                                                          status='income')

                total_amount = 0
                for obj in my_objects:
                    total_amount += obj.amount

                # print("Total Amount:", total_amount)
                # print(my_objects)
                context = {"menu": "menu-income", "income_data": my_objects, "total_amount": total_amount,
                           "start_date": start_date, "end_date": end_date}
                return render(request, 'income/date_filter.html', context)

        elif form_request == 'form2':
            print("form2 working")
            form2 = ACDateForm(request.POST)
            if form2.is_valid():
                date_field = form2.cleaned_data['date_field']
                date_objects = AccountsTable.objects.filter(user=request.user, created_by__date=date_field,
                                                            status="income")
                total_amount = 0
                for obj in date_objects:
                    total_amount += obj.amount
                # print(date_objects)
                context = {"menu": "menu-income", "income_data": date_objects, "total_amount": total_amount,
                           "date_field": date_field}
                return render(request, 'income/day_filter.html', context)

        else:
            month_form = MonthForm(request.POST)
            if month_form.is_valid():
                month = month_form.cleaned_data['month_field']
                year = month_form.cleaned_data['year']
                # print(month)
                # print(year)
                month_objects = AccountsTable.objects.filter(
                    Q(created_by__month=month) & Q(created_by__year=year), status="income", user=request.user
                )
                total_amount = 0
                for obj in month_objects:
                    total_amount += obj.amount
                # print(month_objects)
                context = {"menu": "menu-income", "income_data": month_objects, "total_amount": total_amount,
                           "month": month, "year": year}
                return render(request, 'income/month_filter.html', context)

    context = {"menu": "menu-income", "form": form, "form2": form2, "month_form": month_form}
    return render(request, 'income/filter.html', context)


@login_required
def all_data_download(request):
    obj = AccountsTable.objects.all().order_by('created_by')

    pdf_data = {"ac_table_data": obj}
    template_path = 'download.html'
    template = get_template(template_path)
    html = template.render(pdf_data)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="accounts_report.pdf"'  # Updated line

    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)

    if pisa_status.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisa_status.err, html))

    # Return the PDF response
    response.write(buffer.getvalue())
    buffer.close()
    return response


@login_required
def income_data_download(request):
    obj = AccountsTable.objects.filter(user=request.user, status='income').order_by('created_by')
    total_amount = \
        AccountsTable.objects.filter(user=request.user, status='income').aggregate(total_amount=Sum('amount'))[
            'total_amount']
    pdf_data = {"ac_table_data": obj, "total_amount": total_amount}

    # pdf_data = {"ac_table_data": obj}

    template_path = 'income/download.html'
    template = get_template(template_path)
    html = template.render(pdf_data)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="income_report.pdf"'  # Updated line

    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)

    if pisa_status.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisa_status.err, html))

    # Return the PDF response
    response.write(buffer.getvalue())
    buffer.close()
    return response


@login_required
def expense_data_download(request):
    obj = AccountsTable.objects.filter(user=request.user, status='expense').order_by('created_by')
    total_amount = \
        AccountsTable.objects.filter(user=request.user, status='expense').aggregate(total_amount=Sum('amount'))[
            'total_amount']
    pdf_data = {"ac_table_data": obj, "total_amount": total_amount}

    template_path = 'expense/download.html'
    template = get_template(template_path)
    html = template.render(pdf_data)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expense_report.pdf"'  # Updated line

    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)

    if pisa_status.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisa_status.err, html))

    # Return the PDF response
    response.write(buffer.getvalue())
    buffer.close()
    return response


@login_required
def income_month_download(request, month, year):
    obj = AccountsTable.objects.filter(
        Q(created_by__month=month) & Q(created_by__year=year), status="income", user=request.user
    )

    # print(obj)
    total_amount = AccountsTable.objects.filter(
        Q(created_by__month=month) & Q(created_by__year=year), status="income", user=request.user
    ).aggregate(total_amount=Sum('amount'))['total_amount']

    pdf_data = {"ac_table_data": obj, "total_amount": total_amount, "month": month, "year": str(year)}

    template_path = 'income/month_pdf_download.html'
    template = get_template(template_path)
    html = template.render(pdf_data)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{month} / {year}.pdf'  # Updated line

    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)

    if pisa_status.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisa_status.err, html))

    # Return the PDF response
    response.write(buffer.getvalue())
    buffer.close()
    return response


@login_required
def date_range_income_download(request, start_date, end_date):
    obj = AccountsTable.objects.filter(user=request.user, created_by__range=(start_date, end_date), status='income')
    # print(obj)
    total_amount = AccountsTable.objects.filter(user=request.user, created_by__range=(start_date, end_date),
                                                status='income').aggregate(
        total_amount=Sum('amount'))['total_amount']

    pdf_data = {"ac_table_data": obj, "total_amount": total_amount, "start_date": start_date, "end_date": end_date}

    template_path = 'income/date_range_pdf.html'
    template = get_template(template_path)
    html = template.render(pdf_data)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{start_date} To {end_date}.pdf'  # Updated line

    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)

    if pisa_status.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisa_status.err, html))

    # Return the PDF response
    response.write(buffer.getvalue())
    buffer.close()
    return response


@login_required
def income_date_filter_download(request, date_field):
    obj = AccountsTable.objects.filter(user=request.user, created_by__date=date_field, status="income")
    total_amount = \
        AccountsTable.objects.filter(user=request.user, created_by__date=date_field, status="income").aggregate(
            total_amount=Sum('amount'))['total_amount']
    pdf_data = {"ac_table_data": obj, "total_amount": total_amount, "date_field": date_field}

    template_path = 'income/date_pdf_download.html'
    template = get_template(template_path)
    html = template.render(pdf_data)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{date_field}.pdf"'  # Updated line

    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)

    if pisa_status.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisa_status.err, html))

    # Return the PDF response
    response.write(buffer.getvalue())
    buffer.close()
    return response


# -----------------------

@login_required
def expense_month_download(request, month, year):
    obj = AccountsTable.objects.filter(
        Q(created_by__month=month) & Q(created_by__year=year), status="expense", user=request.user
    )

    # print(obj)
    total_amount = AccountsTable.objects.filter(
        Q(created_by__month=month) & Q(created_by__year=year), status="expense", user=request.user
    ).aggregate(total_amount=Sum('amount'))['total_amount']

    pdf_data = {"ac_table_data": obj, "total_amount": total_amount, "month": month, "year": str(year)}

    template_path = 'expense/month_pdf_download.html'
    template = get_template(template_path)
    html = template.render(pdf_data)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{month} / {year}.pdf'  # Updated line

    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)

    if pisa_status.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisa_status.err, html))

    # Return the PDF response
    response.write(buffer.getvalue())
    buffer.close()
    return response


@login_required
def date_range_expense_download(request, start_date, end_date):
    obj = AccountsTable.objects.filter(user=request.user, created_by__range=(start_date, end_date), status='expense')
    # print(obj)
    total_amount = AccountsTable.objects.filter(user=request.user, created_by__range=(start_date, end_date),
                                                status='expense').aggregate(
        total_amount=Sum('amount'))['total_amount']

    pdf_data = {"ac_table_data": obj, "total_amount": total_amount, "start_date": start_date, "end_date": end_date}

    template_path = 'expense/date_range_pdf.html'
    template = get_template(template_path)
    html = template.render(pdf_data)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{start_date} To {end_date}.pdf'  # Updated line

    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)

    if pisa_status.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisa_status.err, html))

    # Return the PDF response
    response.write(buffer.getvalue())
    buffer.close()
    return response


@login_required
def expense_date_filter_download(request, date_field):
    obj = AccountsTable.objects.filter(user=request.user, created_by__date=date_field, status="expense")
    total_amount = \
        AccountsTable.objects.filter(user=request.user, created_by__date=date_field, status="expense").aggregate(
            total_amount=Sum('amount'))['total_amount']
    pdf_data = {"ac_table_data": obj, "total_amount": total_amount, "date_field": date_field}

    template_path = 'expense/date_pdf_download.html'
    template = get_template(template_path)
    html = template.render(pdf_data)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{date_field}.pdf"'  # Updated line

    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)

    if pisa_status.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisa_status.err, html))

    # Return the PDF response
    response.write(buffer.getvalue())
    buffer.close()
    return response


@login_required
def savings_amount(request):
    obj = AccountsTable.objects.filter(user=request.user, amount_status='savings').order_by('-updated_by')

    income = AccountsTable.objects.filter(user=request.user, status='income', amount_status='savings')
    expense = AccountsTable.objects.filter(user=request.user, status='expense', amount_status='savings')

    income_saving = income.aggregate(income_saving=Sum('amount'))['income_saving'] or 0
    expense_saving = expense.aggregate(expense_saving=Sum('amount'))['expense_saving'] or 0

    total = income_saving - expense_saving

    context = {"savings_data": obj, "menu": "menu-savings", "savings": total}
    return render(request, 'saving/savings_data.html', context)


@login_required
def savings_data_download(request):
    obj = AccountsTable.objects.filter(user=request.user, amount_status='savings').order_by('created_by')

    income = AccountsTable.objects.filter(user=request.user, status='income', amount_status='savings')
    expense = AccountsTable.objects.filter(user=request.user, status='expense', amount_status='savings')

    income_saving = income.aggregate(income_saving=Sum('amount'))['income_saving'] or 0
    expense_saving = expense.aggregate(expense_saving=Sum('amount'))['expense_saving'] or 0

    total_amount = income_saving - expense_saving

    pdf_data = {"saving_table_data": obj, "total_amount": total_amount}

    template_path = 'saving/download.html'
    template = get_template(template_path)
    html = template.render(pdf_data)

    # Create a PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="savings_report.pdf"'  # Updated line

    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)

    if pisa_status.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisa_status.err, html))

    response.write(buffer.getvalue())
    buffer.close()
    return response



