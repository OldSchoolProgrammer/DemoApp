from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    TemplateView, ListView, DetailView, 
    CreateView, UpdateView, DeleteView, FormView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Q, F
from django.db.models.functions import Coalesce

from .models import JewelryItem, Category, Supplier, StockTransaction
from .forms import (
    JewelryItemForm, CategoryForm, SupplierForm, 
    StockAdjustmentForm, ItemSearchForm
)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard with inventory statistics and alerts."""
    template_name = 'inventory/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Basic stats
        context['total_items'] = JewelryItem.objects.filter(is_active=True).count()
        context['total_categories'] = Category.objects.count()
        context['total_suppliers'] = Supplier.objects.count()
        
        # Stock value calculation
        items = JewelryItem.objects.filter(is_active=True)
        total_value = sum(item.stock_value for item in items)
        context['total_stock_value'] = total_value
        
        # Low stock items (quantity <= 5)
        context['low_stock_items'] = JewelryItem.objects.filter(
            is_active=True, 
            quantity__lte=5
        ).order_by('quantity')[:5]
        
        context['low_stock_count'] = JewelryItem.objects.filter(
            is_active=True, 
            quantity__lte=5
        ).count()
        
        # Out of stock count
        context['out_of_stock_count'] = JewelryItem.objects.filter(
            is_active=True, 
            quantity=0
        ).count()
        
        # Recent transactions
        context['recent_transactions'] = StockTransaction.objects.select_related(
            'item', 'user'
        ).order_by('-created_at')[:10]
        
        # Category breakdown
        context['category_stats'] = Category.objects.annotate(
            item_count=Count('items', filter=Q(items__is_active=True)),
            total_quantity=Coalesce(Sum('items__quantity', filter=Q(items__is_active=True)), 0)
        ).order_by('-item_count')[:5]
        
        # Recently added items
        context['recent_items'] = JewelryItem.objects.filter(
            is_active=True
        ).order_by('-created_at')[:5]
        
        return context


class ItemListView(LoginRequiredMixin, ListView):
    """List all jewelry items with search and filtering."""
    model = JewelryItem
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_queryset(self):
        queryset = JewelryItem.objects.filter(is_active=True).select_related(
            'category', 'supplier'
        )
        
        # Search query
        query = self.request.GET.get('query', '')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(sku__icontains=query) |
                Q(description__icontains=query)
            )
        
        # Category filter
        category = self.request.GET.get('category', '')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Metal type filter
        metal_type = self.request.GET.get('metal_type', '')
        if metal_type:
            queryset = queryset.filter(metal_type=metal_type)
        
        # Stock status filter
        stock_status = self.request.GET.get('stock_status', '')
        if stock_status == 'in_stock':
            queryset = queryset.filter(quantity__gt=5)
        elif stock_status == 'low_stock':
            queryset = queryset.filter(quantity__gt=0, quantity__lte=5)
        elif stock_status == 'out_of_stock':
            queryset = queryset.filter(quantity=0)
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ItemSearchForm(self.request.GET)
        context['total_count'] = self.get_queryset().count()
        return context


class ItemDetailView(LoginRequiredMixin, DetailView):
    """View details of a single jewelry item."""
    model = JewelryItem
    template_name = 'inventory/item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transactions'] = self.object.transactions.select_related(
            'user'
        ).order_by('-created_at')[:10]
        return context


class ItemCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create a new jewelry item."""
    model = JewelryItem
    form_class = JewelryItemForm
    template_name = 'inventory/item_form.html'
    success_message = "%(name)s was created successfully!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Jewelry Item'
        context['icon'] = 'bi-plus-circle'
        return context


class ItemUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Update an existing jewelry item."""
    model = JewelryItem
    form_class = JewelryItemForm
    template_name = 'inventory/item_form.html'
    success_message = "%(name)s was updated successfully!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit: {self.object.name}'
        context['icon'] = 'bi-pencil'
        return context


class ItemDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a jewelry item."""
    model = JewelryItem
    template_name = 'inventory/item_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_list')

    def form_valid(self, form):
        messages.success(self.request, f'{self.object.name} was deleted successfully!')
        return super().form_valid(form)


# Category Views
class CategoryListView(LoginRequiredMixin, ListView):
    """List all categories."""
    model = Category
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.annotate(
            item_count=Count('items', filter=Q(items__is_active=True))
        ).order_by('name')


class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create a new category."""
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_message = "Category '%(name)s' was created successfully!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Category'
        return context


class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Update an existing category."""
    model = Category
    form_class = CategoryForm
    template_name = 'inventory/category_form.html'
    success_message = "Category '%(name)s' was updated successfully!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Category: {self.object.name}'
        return context


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a category."""
    model = Category
    template_name = 'inventory/category_confirm_delete.html'
    success_url = reverse_lazy('inventory:category_list')

    def form_valid(self, form):
        messages.success(self.request, f'Category "{self.object.name}" was deleted!')
        return super().form_valid(form)


# Supplier Views
class SupplierListView(LoginRequiredMixin, ListView):
    """List all suppliers."""
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'

    def get_queryset(self):
        return Supplier.objects.annotate(
            item_count=Count('items', filter=Q(items__is_active=True))
        ).order_by('name')


class SupplierCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Create a new supplier."""
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_message = "Supplier '%(name)s' was created successfully!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Supplier'
        return context


class SupplierUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Update an existing supplier."""
    model = Supplier
    form_class = SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_message = "Supplier '%(name)s' was updated successfully!"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit Supplier: {self.object.name}'
        return context


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a supplier."""
    model = Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_list')

    def form_valid(self, form):
        messages.success(self.request, f'Supplier "{self.object.name}" was deleted!')
        return super().form_valid(form)


# Stock Management Views
class StockAdjustmentView(LoginRequiredMixin, FormView):
    """Adjust stock levels."""
    template_name = 'inventory/stock_adjustment.html'
    form_class = StockAdjustmentForm
    success_url = reverse_lazy('inventory:dashboard')

    def form_valid(self, form):
        StockTransaction.objects.create(
            item=form.cleaned_data['item'],
            user=self.request.user,
            transaction_type=form.cleaned_data['transaction_type'],
            quantity=form.cleaned_data['quantity'],
            notes=form.cleaned_data['notes']
        )
        messages.success(
            self.request, 
            f"Stock adjusted for {form.cleaned_data['item'].name}"
        )
        return super().form_valid(form)


class StockHistoryView(LoginRequiredMixin, ListView):
    """View all stock transactions."""
    model = StockTransaction
    template_name = 'inventory/stock_history.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        return StockTransaction.objects.select_related(
            'item', 'user'
        ).order_by('-created_at')


# Reports View
class ReportsView(LoginRequiredMixin, TemplateView):
    """Generate inventory reports."""
    template_name = 'inventory/reports.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Inventory value by category
        context['category_values'] = Category.objects.annotate(
            total_items=Count('items', filter=Q(items__is_active=True)),
            total_quantity=Coalesce(Sum('items__quantity', filter=Q(items__is_active=True)), 0),
        ).filter(total_items__gt=0)
        
        # Calculate values manually
        categories_with_values = []
        for cat in context['category_values']:
            items = JewelryItem.objects.filter(category=cat, is_active=True)
            value = sum(item.stock_value for item in items)
            categories_with_values.append({
                'name': cat.name,
                'total_items': cat.total_items,
                'total_quantity': cat.total_quantity,
                'total_value': value
            })
        context['categories_with_values'] = categories_with_values
        
        # Low stock report
        context['low_stock_items'] = JewelryItem.objects.filter(
            is_active=True,
            quantity__lte=5
        ).select_related('category', 'supplier').order_by('quantity')
        
        # High value items
        context['high_value_items'] = JewelryItem.objects.filter(
            is_active=True
        ).order_by('-selling_price')[:10]
        
        # Metal type breakdown
        context['metal_breakdown'] = JewelryItem.objects.filter(
            is_active=True
        ).exclude(metal_type='').values('metal_type').annotate(
            count=Count('id'),
            total_quantity=Sum('quantity')
        ).order_by('-count')
        
        return context
