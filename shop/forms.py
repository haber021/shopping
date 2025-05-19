from django import forms
from .models import (
    Product, Order, Customer, InventoryTransaction, Supplier, Category, 
    Setting, CustomerDashboardPreference
)
from django.contrib.auth.models import User

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'cost_price', 
                  'stock', 'reorder_level', 'supplier', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address', 'loyalty_points']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'status', 'shipping_address', 'payment_method', 'notes']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class OrderItemForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all())
    quantity = forms.IntegerField(min_value=1)
    
    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        
        if product and quantity:
            if quantity > product.stock:
                raise forms.ValidationError(f"Not enough stock. Only {product.stock} available.")
        return cleaned_data

class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class RestockForm(forms.ModelForm):
    class Meta:
        model = InventoryTransaction
        fields = ['product', 'quantity', 'reference', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        product_id = kwargs.pop('product_id', None)
        super().__init__(*args, **kwargs)
        if product_id:
            self.fields['product'].initial = product_id
            self.fields['product'].widget.attrs['readonly'] = True
        self.fields['transaction_type'] = forms.CharField(
            initial='restock', 
            widget=forms.HiddenInput()
        )

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

class GeneralSettingsForm(forms.Form):
    company_name = forms.CharField(max_length=100)
    company_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    company_email = forms.EmailField()
    company_phone = forms.CharField(max_length=20)

class PaymentSettingsForm(forms.Form):
    tax_rate = forms.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage (%)")
    payment_methods = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), 
                                       help_text="Enter one payment method per line")

class ShippingSettingsForm(forms.Form):
    shipping_methods = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}),
                                       help_text="Enter one shipping method per line")
    default_shipping_fee = forms.DecimalField(max_digits=10, decimal_places=2)

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff']
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

class CustomerDashboardPreferenceForm(forms.ModelForm):
    class Meta:
        model = CustomerDashboardPreference
        fields = ['theme', 'layout', 'show_welcome']
        widgets = {
            'theme': forms.Select(attrs={'class': 'form-select'}),
            'layout': forms.Select(attrs={'class': 'form-select'}),
            'show_welcome': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
class WidgetSettingsForm(forms.Form):
    widget_id = forms.CharField(widget=forms.HiddenInput())
    size = forms.ChoiceField(choices=[
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ], widget=forms.RadioSelect(attrs={'class': 'form-check-input'}))
    collapsed = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    max_items = forms.IntegerField(min_value=1, max_value=10, initial=5, 
                                  widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 80px;'}))

    def __init__(self, *args, **kwargs):
        widget_type = kwargs.pop('widget_type', None)
        super().__init__(*args, **kwargs)
        
        # Some widgets may not need certain settings
        if widget_type and widget_type in ['loyalty_points', 'promotions']:
            self.fields.pop('max_items', None)
