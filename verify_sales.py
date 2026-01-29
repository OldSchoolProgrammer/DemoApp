import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelry_inventory.settings')
django.setup()

from sales.models import Customer, Invoice, InvoiceItem
from sales.services import StripeService, NotificationService
from inventory.models import JewelryItem, Category

def cleanup():
    print("Cleaning up old test data...")
    Customer.objects.filter(email='test@example.com').delete()
    Invoice.objects.filter(customer__email='test@example.com').delete()
    # JewelryItem cleanup if needed, but we'll try to reuse or create temp

def verify_sales_flow():
    cleanup()
    print("\nStarting Sales Flow Verification...")

    # 1. Create Customer
    print("1. Creating Customer...")
    customer = Customer.objects.create(
        name="Test Customer",
        email="test@example.com",
        phone="1234567890",
        address="123 Test St"
    )
    print(f"   Customer created: {customer}")

    # 2. Create Invoice
    print("2. Creating Invoice...")
    invoice = Invoice.objects.create(customer=customer)
    print(f"   Invoice created: {invoice}")

    # 3. Add Items
    print("3. Adding Invoice Items...")
    # Create a dummy inventory item if needed
    category, _ = Category.objects.get_or_create(name="Test Category")
    item, _ = JewelryItem.objects.get_or_create(
        name="Test Ring",
        defaults={
            'category': category,
            'cost_price': 50.00,
            'selling_price': 100.00,
            'quantity': 10
        }
    )
    
    InvoiceItem.objects.create(
        invoice=invoice,
        item=item,
        quantity=1
    )
    # Add a custom item (service)
    InvoiceItem.objects.create(
        invoice=invoice,
        description="Custom Engraving",
        unit_price=25.00,
        quantity=1
    )
    
    print(f"   Items added. Total Amount: €{invoice.total_amount}")
    assert invoice.total_amount == 125.00, f"Expected 125.00, got {invoice.total_amount}"

    # 4. Generate Payment Link
    print("4. Generating Payment Link (Mock)...")
    link = StripeService.create_payment_link(invoice)
    print(f"   Payment Link: {link}")
    assert link is not None, "Payment link should not be None"
    assert "mock" in link or "stripe" in link, "Link looks invalid"

    # 5. Send Email
    print("5. Sending Invoice Email...")
    success = NotificationService.send_invoice_email(invoice)
    print(f"   Email Sent: {success}")
    assert success is True, "Email sending failed"

    print("\nSUCCESS: Sales flow verification passed!")

if __name__ == '__main__':
    try:
        verify_sales_flow()
    except Exception as e:
        print(f"\nFAILURE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
