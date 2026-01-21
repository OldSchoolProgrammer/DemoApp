import os
from io import BytesIO
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.base import ContentFile


class Category(models.Model):
    """Category for organizing jewelry items (e.g., Rings, Necklaces, Bracelets)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('inventory:category_list')


class Supplier(models.Model):
    """Jewelry supplier/vendor information."""
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('inventory:supplier_list')


class JewelryItem(models.Model):
    """Main inventory item model for jewelry pieces."""
    METAL_CHOICES = [
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('platinum', 'Platinum'),
        ('rose_gold', 'Rose Gold'),
        ('white_gold', 'White Gold'),
        ('mixed', 'Mixed Metals'),
        ('other', 'Other'),
    ]

    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU", blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT,
        related_name='items'
    )
    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='items'
    )
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Cost Price (€)"
    )
    selling_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Selling Price (€)"
    )
    quantity = models.PositiveIntegerField(default=0)
    weight_grams = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Weight (grams)"
    )
    metal_type = models.CharField(
        max_length=20, 
        choices=METAL_CHOICES, 
        blank=True
    )
    gemstone = models.CharField(max_length=100, blank=True)
    image = models.ImageField(
        upload_to='jewelry_images/', 
        blank=True, 
        null=True
    )
    barcode_image = models.ImageField(
        upload_to='barcodes/',
        blank=True,
        null=True,
        verbose_name="Barcode Image"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Jewelry Item"
        verbose_name_plural = "Jewelry Items"

    def __str__(self):
        return f"{self.sku} - {self.name}"

    def get_absolute_url(self):
        return reverse('inventory:item_detail', kwargs={'pk': self.pk})

    def generate_sku(self):
        """Generate a unique SKU based on category and auto-increment."""
        # Get category prefix (first 3 letters uppercase)
        category_prefix = self.category.name[:3].upper() if self.category else "GEN"
        
        # Get the next available number
        last_item = JewelryItem.objects.filter(
            sku__startswith=f"JWL-{category_prefix}-"
        ).order_by('-sku').first()
        
        if last_item:
            try:
                # Extract the number from the last SKU
                last_number = int(last_item.sku.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1001
        else:
            next_number = 1001
        
        return f"JWL-{category_prefix}-{next_number}"

    def generate_barcode(self):
        """Generate barcode image from SKU."""
        try:
            import barcode
            from barcode.writer import ImageWriter
            
            # Use Code128 barcode format (good for alphanumeric strings)
            code128 = barcode.get_barcode_class('code128')
            
            # Create barcode with image writer
            barcode_instance = code128(self.sku, writer=ImageWriter())
            
            # Save to BytesIO buffer
            buffer = BytesIO()
            barcode_instance.write(buffer, options={
                'module_width': 0.4,
                'module_height': 15.0,
                'font_size': 10,
                'text_distance': 5.0,
                'quiet_zone': 6.5,
            })
            
            # Create filename
            filename = f"barcode_{self.sku}.png"
            
            # Save to the barcode_image field
            buffer.seek(0)
            self.barcode_image.save(filename, ContentFile(buffer.read()), save=False)
            buffer.close()
            
            return True
        except Exception as e:
            print(f"Error generating barcode: {e}")
            return False

    def save(self, *args, **kwargs):
        """Override save to auto-generate SKU and barcode."""
        # Auto-generate SKU if not provided
        if not self.sku:
            self.sku = self.generate_sku()
        
        # Check if this is a new item or SKU changed
        generate_barcode = False
        if self.pk:
            # Existing item - check if SKU changed
            try:
                old_instance = JewelryItem.objects.get(pk=self.pk)
                if old_instance.sku != self.sku or not self.barcode_image:
                    generate_barcode = True
            except JewelryItem.DoesNotExist:
                generate_barcode = True
        else:
            # New item
            generate_barcode = True
        
        # Save first to get PK if new
        super().save(*args, **kwargs)
        
        # Generate barcode after save (so SKU is finalized)
        if generate_barcode and not self.barcode_image:
            if self.generate_barcode():
                # Save again to update barcode_image field
                super().save(update_fields=['barcode_image'])

    @property
    def profit_margin(self):
        """Calculate profit margin percentage."""
        if self.cost_price and self.cost_price > 0:
            return round(((self.selling_price - self.cost_price) / self.cost_price) * 100, 2)
        return 0

    @property
    def stock_value(self):
        """Calculate total value of stock at cost price."""
        return self.quantity * self.cost_price

    @property
    def stock_status(self):
        """Return stock status: 'out', 'low', or 'ok'."""
        if self.quantity == 0:
            return 'out'
        elif self.quantity <= 5:
            return 'low'
        return 'ok'


class StockTransaction(models.Model):
    """Track stock movements (in, out, adjustments)."""
    TRANSACTION_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Adjustment'),
    ]

    item = models.ForeignKey(
        JewelryItem, 
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True
    )
    transaction_type = models.CharField(
        max_length=20, 
        choices=TRANSACTION_TYPES
    )
    quantity = models.IntegerField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_transaction_type_display()}: {self.item.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        """Update item quantity when transaction is saved."""
        if not self.pk:  # Only on creation
            if self.transaction_type == 'in':
                self.item.quantity += abs(self.quantity)
            elif self.transaction_type == 'out':
                self.item.quantity -= abs(self.quantity)
            else:  # adjustment
                self.item.quantity += self.quantity
            self.item.save()
        super().save(*args, **kwargs)
