from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset

from .models import (
    Product, Category, Customer, Order, OrderItem, 
    Supplier, Inventory, CompanySettings
)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'supplier']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('category', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('price', css_class='form-group col-md-6 mb-0'),
                Column('supplier', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'description',
        )

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('email', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'address',
        )

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'status', 'shipping_address', 'payment_method']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
        self.helper.layout = Layout(
            Row(
                Column('customer', css_class='form-group col-md-6 mb-0'),
                Column('status', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'shipping_address',
            'payment_method'
        )

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']

OrderItemFormSet = inlineformset_factory(
    Order, OrderItem, form=OrderItemForm,
    extra=1, can_delete=True
)

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('contact_person', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-0'),
                Column('phone', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'address',
        )

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['product', 'current_stock', 'reorder_level']

class RestockForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, label="Quantity to Add")
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Restock'))

class ReportFilterForm(forms.Form):
    REPORT_TYPES = (
        ('sales', 'Sales Report'),
        ('inventory', 'Inventory Report'),
        ('customer', 'Customer Report'),
    )
    
    report_type = forms.ChoiceField(choices=REPORT_TYPES, initial='sales')
    date_from = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('report_type', css_class='form-group col-md-4 mb-0'),
                Column('date_from', css_class='form-group col-md-4 mb-0'),
                Column('date_to', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Generate Report')
        )

class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = CompanySettings
        fields = ['company_name', 'logo', 'address', 'email', 'phone', 'tax_rate']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save Settings'))
        self.helper.layout = Layout(
            Fieldset(
                'Company Information',
                Row(
                    Column('company_name', css_class='form-group col-md-6 mb-0'),
                    Column('logo', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                'address',
                Row(
                    Column('email', css_class='form-group col-md-6 mb-0'),
                    Column('phone', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Fieldset(
                'Financial Settings',
                'tax_rate',
            ),
        )
