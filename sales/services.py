import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

class StripeService:
    @staticmethod
    def create_payment_link(invoice):
        """
        Creates a Stripe Payment Link for the invoice.
        """
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            # Create line items for Stripe
            line_items = []
            for item in invoice.items.all():
                line_items.append({
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': item.description,
                        },
                        'unit_amount': int(item.unit_price * 100),  # Stripe expects cents
                    },
                    'quantity': item.quantity,
                })
            
            if not line_items:
                return None

            # Create payment link
            payment_link = stripe.PaymentLink.create(
                line_items=line_items,
                metadata={'invoice_id': invoice.id},
                after_completion={
                    'type': 'redirect',
                    'redirect': {
                        # Redirect back to a success page (needs to be implemented/configured)
                        'url': 'http://localhost:8000/sales/invoice/success/', # TODO: make dynamic
                    },
                }
            )
            
            # Update invoice with link
            invoice.stripe_payment_link = payment_link.url
            invoice.save()
            
            return payment_link.url
            
        except Exception as e:
            print(f"Stripe Error: {e}")
            # For development/demo without keys, return a mock link if configured to do so
            if settings.DEBUG:
                invoice.stripe_payment_link = f"https://checkout.stripe.com/mock/{invoice.id}"
                invoice.save()
                return invoice.stripe_payment_link
            return None

class NotificationService:
    @staticmethod
    def send_invoice_email(invoice):
        """
        Sends an email with the invoice details and payment link.
        Returns tuple: (success: bool, error_message: str or None)
        """
        if not invoice.customer.email:
            return (False, "Customer has no email address")
            
        subject = f"Invoice #{invoice.id} from Jewelry Store"
        message = f"""
Dear {invoice.customer.name},

Please find your invoice #{invoice.id}.
Total Amount: €{invoice.total_amount}

You can pay securely online using the following link:
{invoice.stripe_payment_link or 'Link generation pending'}

Thank you for your business!
        """
        
        try:
            send_mail(
                subject,
                message.strip(),
                settings.DEFAULT_FROM_EMAIL,
                [invoice.customer.email],
                fail_silently=False,
            )
            return (True, None)
        except Exception as e:
            error_msg = str(e)
            print(f"Email Error: {error_msg}")
            return (False, error_msg)

    @staticmethod
    def send_invoice_sms(invoice):
        """
        Sends an SMS with the payment link.
        """
        if not invoice.customer.phone:
            return False
            
        # Placeholder for SMS provider logic (e.g. Twilio)
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(...)
        
        print(f"SIMULATED SMS to {invoice.customer.phone}: Pay your invoice here: {invoice.stripe_payment_link}")
        return True
