from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import stripe
import json

from .models import Customer, Invoice, InvoiceItem
from .forms import CustomerForm, InvoiceForm, InvoiceItemForm
from .services import StripeService, NotificationService
from inventory.models import JewelryItem

# ==================== Customer Views ====================

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'sales/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 10

class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'sales/customer_detail.html'
    context_object_name = 'customer'

class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'sales/customer_form.html'
    success_url = reverse_lazy('sales:customer_list')

    def form_valid(self, form):
        messages.success(self.request, 'Customer created successfully!')
        return super().form_valid(form)

class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'sales/customer_form.html'
    success_url = reverse_lazy('sales:customer_list')

    def form_valid(self, form):
        messages.success(self.request, 'Customer updated successfully!')
        return super().form_valid(form)

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'sales/customer_confirm_delete.html'
    success_url = reverse_lazy('sales:customer_list')

# ==================== Invoice Views ====================

class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'sales/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 10

class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'sales/invoice_detail.html'
    context_object_name = 'invoice'

class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'sales/invoice_form.html'

    def get_success_url(self):
        return reverse('sales:invoice_add_items', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Invoice created! Now add items.')
        return super().form_valid(form)

@login_required
def invoice_add_items(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    items = JewelryItem.objects.filter(is_active=True, quantity__gt=0)
    
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        description = request.POST.get('description')
        quantity = int(request.POST.get('quantity', 1))
        unit_price = request.POST.get('unit_price')
        
        if item_id:
            jewelry_item = get_object_or_404(JewelryItem, pk=item_id)
            InvoiceItem.objects.create(
                invoice=invoice,
                item=jewelry_item,
                description=jewelry_item.name,
                quantity=quantity,
                unit_price=jewelry_item.selling_price
            )
        elif description and unit_price:
            InvoiceItem.objects.create(
                invoice=invoice,
                description=description,
                quantity=quantity,
                unit_price=unit_price
            )
        messages.success(request, 'Item added to invoice!')
        return redirect('sales:invoice_add_items', pk=pk)
    
    return render(request, 'sales/invoice_add_items.html', {
        'invoice': invoice,
        'items': items,
    })

@login_required
def invoice_remove_item(request, pk, item_pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    item = get_object_or_404(InvoiceItem, pk=item_pk, invoice=invoice)
    item.delete()
    messages.success(request, 'Item removed from invoice.')
    return redirect('sales:invoice_add_items', pk=pk)

@login_required
def invoice_generate_payment_link(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if invoice.items.count() == 0:
        messages.error(request, 'Cannot generate payment link for empty invoice.')
        return redirect('sales:invoice_detail', pk=pk)
    
    link = StripeService.create_payment_link(invoice)
    
    if link:
        invoice.status = 'sent'
        invoice.save()
        messages.success(request, f'Payment link generated: {link}')
    else:
        messages.error(request, 'Failed to generate payment link.')
    
    return redirect('sales:invoice_detail', pk=pk)

@login_required
def invoice_send_email(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if not invoice.stripe_payment_link:
        messages.error(request, 'Generate a payment link first.')
        return redirect('sales:invoice_detail', pk=pk)
    
    success, error_msg = NotificationService.send_invoice_email(invoice)
    
    if success:
        messages.success(request, f'Invoice email sent to {invoice.customer.email}')
    else:
        messages.error(request, f'Failed to send email: {error_msg}')
    
    return redirect('sales:invoice_detail', pk=pk)

@login_required
def invoice_send_sms(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    
    if not invoice.stripe_payment_link:
        messages.error(request, 'Generate a payment link first.')
        return redirect('sales:invoice_detail', pk=pk)
    
    success, error_msg = NotificationService.send_invoice_sms(invoice)
    
    if success:
        messages.success(request, f'Invoice SMS sent to {invoice.customer.phone}')
    else:
        messages.error(request, f'Failed to send SMS: {error_msg}')
    
    return redirect('sales:invoice_detail', pk=pk)

def invoice_success(request):
    return render(request, 'sales/invoice_success.html')

# ==================== Stripe Webhook ====================

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        invoice_id = session.get('metadata', {}).get('invoice_id')
        
        if invoice_id:
            try:
                invoice = Invoice.objects.get(pk=invoice_id)
                invoice.status = 'paid'
                invoice.stripe_payment_intent = session.get('payment_intent')
                invoice.save()
            except Invoice.DoesNotExist:
                pass
    
    elif event['type'] == 'payment_link.created':
        # Log or handle payment link creation
        pass
    
    return HttpResponse(status=200)
