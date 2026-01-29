from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Customer URLs
    path('customers/', views.CustomerListView.as_view(), name='customer_list'),
    path('customers/add/', views.CustomerCreateView.as_view(), name='customer_create'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer_detail'),
    path('customers/<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer_update'),
    path('customers/<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='customer_delete'),
    
    # Invoice URLs
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/add/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/add-items/', views.invoice_add_items, name='invoice_add_items'),
    path('invoices/<int:pk>/remove-item/<int:item_pk>/', views.invoice_remove_item, name='invoice_remove_item'),
    path('invoices/<int:pk>/generate-link/', views.invoice_generate_payment_link, name='invoice_generate_link'),
    path('invoices/<int:pk>/send-email/', views.invoice_send_email, name='invoice_send_email'),
    path('invoices/<int:pk>/send-sms/', views.invoice_send_sms, name='invoice_send_sms'),
    path('invoice/success/', views.invoice_success, name='invoice_success'),
    
    # Stripe Webhook
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
