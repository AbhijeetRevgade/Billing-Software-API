import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = 'Seeds the database with common firecracker products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of products to generate (default 50)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        brands = ['Standard', 'Kaliswari', 'Arasan', 'Sri Krishna', 'Sony', 'Anil', 'Supreme']
        
        categories = [
            'Sparklers', 'Flower Pots', 'Ground Spinners', 'Rockets', 
            'Garlands', 'Fancy Crackers', 'Bijli Crackers', 'Atom Bombs'
        ]
        
        product_templates = [
            # Sparklers (Fulbajhis)
            "7cm Sparkler", "10cm Sparkler", "12cm Gold Sparkler", "15cm Electric Sparkler", "30cm Jumbo Sparkler", "Magic Wand Sparkler",
            # Flower Pots (Anars)
            "Flower Pot Big", "Flower Pot Special", "Flower Pot Giant", "Flower Pot Red Currants", "Flower Pot Green Leaves", "Aakash Tara Anar",
            # Ground Spinners (Chakkars)
            "Ground Wheel Small", "Ground Wheel Big", "Chakkar Special", "Zameen Chakkar Power", "Deluxe Spinners",
            # Garlands (Maals)
            "100 Garlands (Laxmi Maal)", "1000 Garlands", "2000 Garlands", "5000 Garlands", "10000 Garlands", "28 Deluxe Maal", "56 Deluxe Maal",
            # Fancy / Multi-shots
            "7 Shot Fancy", "12 Shot Multi-colour", "30 Shot Sky Shot", "60 Shot Special", "120 Shot Magic", "240 Shot Mega",
            "Whistling Rocket", "Para-shoot Rocket", "Double Sound Shell",
            # Bombs
            "Atom Bomb Special", "Classic Hydro Bomb", "King of Kings", "Sultan Bomb",
            # Loose/Bijli
            "Bijli Crackers (Strip)", "Bullet Crackers", "Laxmi Bomb", "Red Bijli (Pack of 50)"
        ]

        # Use bulk_create for performance
        products_to_create = []
        created_count = 0

        self.stdout.write(self.style.SUCCESS(f'Generating {count} products (Vighnaharta Fataka Inventory)...'))

        for i in range(count):
            template_name = random.choice(product_templates)
            brand = random.choice(brands)
            name = f"{template_name} - {brand}" if random.choice([True, False]) else template_name
            
            # Weighted random branding
            if random.random() < 0.2:
                name = f"Vighnaharta Special - {template_name}"

            # Pricing logic
            base_price = Decimal(random.randint(20, 1500))
            mrp = base_price * Decimal(random.uniform(1.5, 2.5))
            selling_price = mrp * Decimal(0.8) # 20% discount on MRP
            purchase_price = selling_price * Decimal(0.5) # 50% margin
            
            # Simple stock levels
            stock = random.randint(0, 500)
            min_stock = random.randint(5, 20)

            product = Product(
                name=name,
                brand=brand,
                purchase_price=purchase_price.quantize(Decimal('0.00')),
                selling_price=selling_price.quantize(Decimal('0.00')),
                mrp=mrp.quantize(Decimal('0.00')),
                stock_quantity=stock,
                min_stock_level=min_stock,
                is_active=True
            )
            # We don't specify SKU here, the save() method in models handles it,
            # BUT bulk_create doesn't call save().
            # So I will generate the SKU manually here to avoid issues and benefit from bulk create.
            # However, the model has a nice generate_unique_sku function.
            products_to_create.append(product)

        # Because bulk_create doesn't call .save(), we need to manually trigger SKU generation if we use it.
        # Alternatively, for 100 products, calling .save() in a loop is fine. 
        # But for 1000s, bulk_create is better.
        
        from products.models import generate_unique_sku
        
        used_skus = set()
        for p in products_to_create:
            while True:
                sku = generate_unique_sku()
                if sku not in used_skus:
                    p.sku = sku
                    used_skus.add(sku)
                    break

        # Perform bulk creation
        Product.objects.bulk_create(products_to_create)

        self.stdout.write(self.style.SUCCESS(f'Successfully added {count} products!'))
