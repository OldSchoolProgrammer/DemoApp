from django.db import models
from django.urls import reverse
from inventory.models import JewelryItem
import uuid

class Customer(models.Model):
    """Customer information for sales and invoicing."""
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Invoice(models.Model):
    """Invoice for a customer transaction."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='invoices')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    stripe_payment_link = models.URLField(blank=True, null=True, help_text="Stripe Payment Link URL")
    stripe_payment_intent = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice #{self.pk} - {self.customer.name}"
    
    @property
    def total_amount(self):
        """Calculate total amount from invoice items."""
        return sum(item.total_price for item in self.items.all())

class InvoiceItem(models.Model):
    """Line item for an invoice."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(JewelryItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice_items')
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} ({self.quantity})"
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        # Auto-fill description/price if linked to inventory item and not set
        if self.item and not self.description:
            self.description = self.item.name
        if self.item and not self.unit_price:
            self.unit_price = self.item.selling_price
        super().save(*args, **kwargs)
