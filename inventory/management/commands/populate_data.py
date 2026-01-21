"""
Management command to populate the database with realistic jewelry store dummy data.
"""
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import Category, Supplier, JewelryItem, StockTransaction


class Command(BaseCommand):
    help = 'Populate database with dummy jewelry inventory data'

    def handle(self, *args, **options):
        self.stdout.write('Creating dummy data for Jewelry Inventory...\n')
        
        # Create categories
        categories_data = [
            ('Rings', 'Engagement rings, wedding bands, fashion rings, and signet rings'),
            ('Necklaces', 'Pendants, chains, chokers, and statement necklaces'),
            ('Bracelets', 'Bangles, charm bracelets, tennis bracelets, and cuffs'),
            ('Earrings', 'Studs, hoops, drop earrings, and chandelier earrings'),
            ('Watches', 'Luxury watches, dress watches, and smart watches'),
            ('Brooches', 'Vintage brooches, pins, and decorative accessories'),
            ('Anklets', 'Chain anklets, beaded anklets, and charm anklets'),
            ('Pendants', 'Diamond pendants, gemstone pendants, and lockets'),
        ]
        
        categories = []
        for name, desc in categories_data:
            cat, created = Category.objects.get_or_create(name=name, defaults={'description': desc})
            categories.append(cat)
            if created:
                self.stdout.write(f'  Created category: {name}')
        
        # Create suppliers
        suppliers_data = [
            ('Diamond Dreams Ltd', 'Michael Chen', 'michael@diamonddreams.com', '+1-555-0101', '123 Diamond Row, New York, NY 10001'),
            ('Golden Touch Jewelry', 'Sarah Johnson', 'sarah@goldentouch.com', '+1-555-0102', '456 Gold Avenue, Los Angeles, CA 90001'),
            ('Sapphire & Co.', 'James Williams', 'james@sapphireco.com', '+1-555-0103', '789 Gem Street, Chicago, IL 60601'),
            ('Platinum Plus', 'Emma Davis', 'emma@platinumplus.com', '+1-555-0104', '321 Platinum Lane, Miami, FL 33101'),
            ('Ruby Red Imports', 'Robert Brown', 'robert@rubyred.com', '+1-555-0105', '654 Ruby Road, Houston, TX 77001'),
            ('Silver Stream Jewelry', 'Lisa Anderson', 'lisa@silverstream.com', '+1-555-0106', '987 Silver Way, Seattle, WA 98101'),
            ('Emerald Excellence', 'David Martinez', 'david@emeraldex.com', '+1-555-0107', '147 Emerald Blvd, Boston, MA 02101'),
            ('Pearl Paradise', 'Jennifer Wilson', 'jennifer@pearlparadise.com', '+1-555-0108', '258 Pearl Street, San Francisco, CA 94101'),
        ]
        
        suppliers = []
        for name, contact, email, phone, address in suppliers_data:
            sup, created = Supplier.objects.get_or_create(
                name=name,
                defaults={
                    'contact_person': contact,
                    'email': email,
                    'phone': phone,
                    'address': address
                }
            )
            suppliers.append(sup)
            if created:
                self.stdout.write(f'  Created supplier: {name}')
        
        # Jewelry item templates for realistic data
        jewelry_templates = {
            'Rings': [
                ('Diamond Solitaire Ring', 'diamond', 'Classic solitaire engagement ring with brilliant cut diamond'),
                ('Gold Wedding Band', 'gold', 'Traditional 14K gold wedding band'),
                ('Rose Gold Eternity Ring', 'rose_gold', 'Elegant eternity ring with channel-set diamonds'),
                ('Platinum Diamond Ring', 'platinum', 'Premium platinum ring with princess cut diamond'),
                ('Silver Stackable Ring', 'silver', 'Minimalist sterling silver stacking ring'),
                ('White Gold Halo Ring', 'white_gold', 'Stunning halo engagement ring'),
                ('Vintage Art Deco Ring', 'gold', 'Art deco inspired vintage style ring'),
                ('Three Stone Diamond Ring', 'platinum', 'Past, present, future three stone design'),
            ],
            'Necklaces': [
                ('Diamond Pendant Necklace', 'white_gold', 'Delicate solitaire diamond pendant'),
                ('Gold Chain Necklace', 'gold', '18K gold Cuban link chain'),
                ('Pearl Strand Necklace', 'gold', 'Freshwater pearl strand with gold clasp'),
                ('Silver Heart Pendant', 'silver', 'Sterling silver heart pendant necklace'),
                ('Rose Gold Layered Necklace', 'rose_gold', 'Trendy layered chain necklace'),
                ('Emerald Drop Necklace', 'gold', 'Stunning emerald drop pendant'),
                ('Tennis Necklace', 'white_gold', 'Classic diamond tennis necklace'),
                ('Sapphire Station Necklace', 'platinum', 'Elegant sapphire by-the-yard style'),
            ],
            'Bracelets': [
                ('Diamond Tennis Bracelet', 'white_gold', 'Brilliant cut diamond tennis bracelet'),
                ('Gold Bangle Bracelet', 'gold', 'Classic hollow gold bangle'),
                ('Charm Bracelet', 'silver', 'Sterling silver link charm bracelet'),
                ('Cuff Bracelet', 'rose_gold', 'Wide rose gold cuff bracelet'),
                ('Pearl Bracelet', 'gold', 'Freshwater pearl strand bracelet'),
                ('Chain Link Bracelet', 'platinum', 'Heavy platinum chain link'),
                ('Gemstone Bracelet', 'gold', 'Multi-colored gemstone tennis style'),
                ('Leather & Gold Wrap', 'mixed', 'Leather wrap with gold accents'),
            ],
            'Earrings': [
                ('Diamond Stud Earrings', 'white_gold', 'Classic round brilliant diamond studs'),
                ('Gold Hoop Earrings', 'gold', 'Medium sized 14K gold hoops'),
                ('Pearl Drop Earrings', 'gold', 'Elegant freshwater pearl drops'),
                ('Chandelier Earrings', 'silver', 'Statement crystal chandelier earrings'),
                ('Huggie Hoop Earrings', 'rose_gold', 'Small rose gold huggie hoops'),
                ('Sapphire Studs', 'platinum', 'Natural blue sapphire studs'),
                ('Ruby Drop Earrings', 'gold', 'Pear shaped ruby drops'),
                ('Diamond Cluster Earrings', 'white_gold', 'Floral diamond cluster design'),
            ],
            'Watches': [
                ('Diamond Bezel Watch', 'white_gold', 'Luxury watch with diamond bezel'),
                ('Classic Gold Watch', 'gold', 'Timeless 18K gold dress watch'),
                ('Silver Chronograph', 'silver', 'Stainless steel chronograph'),
                ('Rose Gold Ladies Watch', 'rose_gold', 'Elegant ladies rose gold watch'),
                ('Platinum Limited Edition', 'platinum', 'Limited edition platinum timepiece'),
                ('Two-Tone Bracelet Watch', 'mixed', 'Gold and steel two-tone watch'),
            ],
            'Brooches': [
                ('Vintage Diamond Brooch', 'platinum', 'Art nouveau diamond brooch'),
                ('Gold Flower Brooch', 'gold', 'Detailed floral design brooch'),
                ('Pearl Cluster Brooch', 'gold', 'Pearl and diamond cluster'),
                ('Silver Celtic Brooch', 'silver', 'Traditional Celtic knot design'),
            ],
            'Anklets': [
                ('Gold Chain Anklet', 'gold', 'Delicate 14K gold chain anklet'),
                ('Silver Charm Anklet', 'silver', 'Sterling silver with charms'),
                ('Rose Gold Anklet', 'rose_gold', 'Rose gold link anklet'),
            ],
            'Pendants': [
                ('Diamond Heart Pendant', 'white_gold', 'Pave diamond heart pendant'),
                ('Birthstone Pendant', 'gold', 'Custom birthstone pendant'),
                ('Cross Pendant', 'gold', 'Classic gold cross pendant'),
                ('Locket Pendant', 'silver', 'Vintage style photo locket'),
                ('Initial Pendant', 'rose_gold', 'Personalized initial pendant'),
            ],
        }
        
        # Gemstones for variety
        gemstones = ['Diamond', 'Sapphire', 'Ruby', 'Emerald', 'Pearl', 'Amethyst', 
                     'Topaz', 'Opal', 'Aquamarine', 'Garnet', 'Tanzanite', '']
        
        # Get or create admin user for transactions
        admin_user = User.objects.filter(is_superuser=True).first()
        
        items_created = 0
        sku_counter = 1000
        
        for category in categories:
            if category.name not in jewelry_templates:
                continue
                
            templates = jewelry_templates[category.name]
            
            # Create multiple variations of each template
            for base_name, metal, description in templates:
                # Create 1-3 variations of each template
                variations = random.randint(1, 3)
                
                for v in range(variations):
                    sku_counter += 1
                    sku = f"JWL-{category.name[:3].upper()}-{sku_counter}"
                    
                    # Randomize name slightly
                    size_variants = ['Small', 'Medium', 'Large', 'Petite', 'Statement', '']
                    variant = random.choice(size_variants)
                    name = f"{variant} {base_name}".strip() if variant else base_name
                    
                    # Random pricing based on metal type
                    price_multipliers = {
                        'platinum': (800, 5000),
                        'gold': (300, 3000),
                        'white_gold': (400, 4000),
                        'rose_gold': (350, 3500),
                        'silver': (50, 500),
                        'mixed': (200, 1500),
                        'other': (100, 800),
                    }
                    min_price, max_price = price_multipliers.get(metal, (100, 1000))
                    cost_price = Decimal(random.randint(min_price, max_price))
                    # Markup between 40% and 120%
                    markup = Decimal(random.randint(140, 220)) / 100
                    selling_price = (cost_price * markup).quantize(Decimal('0.01'))
                    
                    # Random quantity
                    quantity = random.randint(0, 25)
                    
                    # Random weight
                    weight = Decimal(random.randint(10, 500) / 10).quantize(Decimal('0.01'))
                    
                    # Random gemstone
                    gemstone = random.choice(gemstones) if random.random() > 0.3 else ''
                    
                    item, created = JewelryItem.objects.get_or_create(
                        sku=sku,
                        defaults={
                            'name': name,
                            'description': description,
                            'category': category,
                            'supplier': random.choice(suppliers),
                            'cost_price': cost_price,
                            'selling_price': selling_price,
                            'quantity': quantity,
                            'weight_grams': weight,
                            'metal_type': metal,
                            'gemstone': gemstone,
                            'is_active': random.random() > 0.05,  # 95% active
                        }
                    )
                    
                    if created:
                        items_created += 1
                        
                        # Create some random transactions for this item (stock-in only to avoid negatives)
                        if admin_user and random.random() > 0.3:
                            num_transactions = random.randint(1, 3)
                            for _ in range(num_transactions):
                                trans_qty = random.randint(1, 5)
                                
                                StockTransaction.objects.create(
                                    item=item,
                                    user=admin_user,
                                    transaction_type='in',
                                    quantity=trans_qty,
                                    notes="Initial stock replenishment"
                                )
        
        self.stdout.write(self.style.SUCCESS(
            f'\nSuccessfully created:\n'
            f'   - {len(categories)} categories\n'
            f'   - {len(suppliers)} suppliers\n'
            f'   - {items_created} jewelry items\n'
            f'   - Multiple stock transactions\n'
        ))
