from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Items
    path('items/', views.ItemListView.as_view(), name='item_list'),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('items/add/', views.ItemCreateView.as_view(), name='item_create'),
    path('items/<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item_update'),
    path('items/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Suppliers
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/add/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    
    # Stock Management
    path('stock/adjust/', views.StockAdjustmentView.as_view(), name='stock_adjust'),
    path('stock/history/', views.StockHistoryView.as_view(), name='stock_history'),
    
    # Reports
    path('reports/', views.ReportsView.as_view(), name='reports'),
]
