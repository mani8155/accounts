from django import forms
from .models import AccountsTable


class ACForm(forms.Form):
    start_date = forms.DateField(label='From ', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='To ', widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super(ACForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class CreateAccountsForm(forms.ModelForm):
    class Meta:
        model = AccountsTable
        fields = ['status', 'amount_status', 'category', 'categorys', 'amount', 'remark']

    def __init__(self, *args, **kwargs):
        super(CreateAccountsForm, self).__init__(*args, **kwargs)

        self.fields['category'].required = False
        self.fields['categorys'].required = False

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class ACDateForm(forms.Form):
    date_field = forms.DateField(label='Date', widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super(ACDateForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class MonthForm(forms.Form):
    # month = forms.DateField(widget=forms.SelectDateWidget(empty_label=("Choose Month")))
    month_field = forms.ChoiceField(label="DB Engine",
                                    choices=[
                                        ('01', 'January'),
                                        ('02', 'February'),
                                        ('03', 'March'),
                                        ('04', 'April'),
                                        ('05', 'May'),
                                        ('06', 'June'),
                                        ('07', 'July'),
                                        ('08', 'August'),
                                        ('09', 'September'),
                                        ('10', 'October'),
                                        ('11', 'November'),
                                        ('12', 'December'),
                                    ])

    YEAR_CHOICES = [(str(year), str(year)) for year in range(2020, 2030)]  # Adjust the range as needed

    year = forms.ChoiceField(choices=YEAR_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(MonthForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
