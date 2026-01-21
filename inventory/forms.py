from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML
from .models import JewelryItem, Category, Supplier, StockTransaction


class JewelryItemForm(forms.ModelForm):
    """Form for creating and updating jewelry items."""
    
    class Meta:
        model = JewelryItem
        fields = [
            'name', 'description', 'category', 'supplier',
            'cost_price', 'selling_price', 'quantity', 'weight_grams',
            'metal_type', 'gemstone', 'image', 'is_active'
        ]
        # Note: SKU and barcode_image are auto-generated and not included
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            HTML('<h5 class="mb-3 text-primary"><i class="bi bi-info-circle"></i> Basic Information</h5>'),
            HTML('<p class="text-muted small mb-3"><i class="bi bi-info-circle me-1"></i>SKU and barcode will be auto-generated when you save.</p>'),
            'name',
            Row(
                Column('category', css_class='col-md-6'),
                Column('supplier', css_class='col-md-6'),
            ),
            'description',
            HTML('<hr class="my-4"><h5 class="mb-3 text-primary"><i class="bi bi-currency-euro"></i> Pricing & Inventory</h5>'),
            Row(
                Column('cost_price', css_class='col-md-4'),
                Column('selling_price', css_class='col-md-4'),
                Column('quantity', css_class='col-md-4'),
            ),
            HTML('<hr class="my-4"><h5 class="mb-3 text-primary"><i class="bi bi-gem"></i> Jewelry Details</h5>'),
            Row(
                Column('metal_type', css_class='col-md-4'),
                Column('gemstone', css_class='col-md-4'),
                Column('weight_grams', css_class='col-md-4'),
            ),
            'image',
            Div(
                'is_active',
                css_class='form-check mt-3'
            ),
            Div(
                Submit('submit', 'Save Item', css_class='btn btn-primary btn-lg me-2'),
                HTML('<a href="{% url \'inventory:item_list\' %}" class="btn btn-outline-secondary btn-lg">Cancel</a>'),
                css_class='mt-4'
            )
        )


class CategoryForm(forms.ModelForm):
    """Form for creating and updating categories."""
    
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'name',
            'description',
            Div(
                Submit('submit', 'Save Category', css_class='btn btn-primary'),
                HTML('<a href="{% url \'inventory:category_list\' %}" class="btn btn-outline-secondary ms-2">Cancel</a>'),
                css_class='mt-3'
            )
        )


class SupplierForm(forms.ModelForm):
    """Form for creating and updating suppliers."""
    
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'email', 'phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-md-6'),
                Column('contact_person', css_class='col-md-6'),
            ),
            Row(
                Column('email', css_class='col-md-6'),
                Column('phone', css_class='col-md-6'),
            ),
            'address',
            Div(
                Submit('submit', 'Save Supplier', css_class='btn btn-primary'),
                HTML('<a href="{% url \'inventory:supplier_list\' %}" class="btn btn-outline-secondary ms-2">Cancel</a>'),
                css_class='mt-3'
            )
        )


class StockAdjustmentForm(forms.Form):
    """Form for adjusting stock levels."""
    
    item = forms.ModelChoiceField(
        queryset=JewelryItem.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    transaction_type = forms.ChoiceField(
        choices=StockTransaction.TRANSACTION_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'item',
            Row(
                Column('transaction_type', css_class='col-md-6'),
                Column('quantity', css_class='col-md-6'),
            ),
            'notes',
            Div(
                Submit('submit', 'Record Transaction', css_class='btn btn-primary'),
                css_class='mt-3'
            )
        )


class ItemSearchForm(forms.Form):
    """Form for searching and filtering items."""
    
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name or SKU...',
            'class': 'form-control'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    metal_type = forms.ChoiceField(
        choices=[('', 'All Metals')] + JewelryItem.METAL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    stock_status = forms.ChoiceField(
        choices=[
            ('', 'All Stock Levels'),
            ('in_stock', 'In Stock (> 5)'),
            ('low_stock', 'Low Stock (≤ 5)'),
            ('out_of_stock', 'Out of Stock'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
