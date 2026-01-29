from django import forms
from .models import Customer, Invoice, InvoiceItem
from inventory.models import JewelryItem
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field, ButtonHolder

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form_group col-md-6 mb-0'),
                Column('email', css_class='form_group col-md-6 mb-0'),
                css_class='form_row'
            ),
            Row(
                Column('phone', css_class='form_group col-md-6 mb-0'),
                Column('address', css_class='form_group col-md-6 mb-0'),
                css_class='form_row'
            ),
            Submit('submit', 'Save Customer')
        )

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['customer', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'customer',
            'due_date',
            Submit('submit', 'Create Invoice')
        )

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['item', 'description', 'quantity', 'unit_price']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
