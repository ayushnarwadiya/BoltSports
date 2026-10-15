from django.core.management.base import BaseCommand
from django.utils.text import slugify

from store.models import Category, Product, Sport

SPORTS = [
    ('Cricket', '🏏'), ('Football', '⚽'), ('Badminton', '🏸'),
    ('Basketball', '🏀'), ('Tennis', '🎾'), ('Fitness', '🏋️'),
    ('Running', '🏃'), ('Table Tennis', '🏓'),
]

CATEGORIES = ['Bats and Rackets', 'Balls', 'Footwear', 'Apparel', 'Protective Gear', 'Accessories']

# (name, sport, category, price, stock, description)
PRODUCTS = [
    ('English Willow Cricket Bat', 'Cricket', 'Bats and Rackets', 4999, 12, 'Full-size English willow bat with a thick edge and a comfortable grip. Suitable for leather-ball matches.'),
    ('Leather Cricket Ball (Pack of 3)', 'Cricket', 'Balls', 899, 40, 'Four-piece leather balls with a tight seam that keeps its shape over many overs.'),
    ('Batting Gloves', 'Cricket', 'Protective Gear', 1299, 25, 'Padded batting gloves with a breathable palm and flexible finger protection.'),
    ('Cricket Helmet', 'Cricket', 'Protective Gear', 1799, 15, 'Lightweight helmet with a steel grille and adjustable back strap.'),
    ('Cricket Shoes', 'Cricket', 'Footwear', 2499, 18, 'Spiked shoes that give a firm grip on the pitch and cushioning for long innings.'),
    ('Size 5 Football', 'Football', 'Balls', 999, 50, 'Machine-stitched size 5 football with a durable outer layer for grass and turf.'),
    ('Studded Football Boots', 'Football', 'Footwear', 2799, 20, 'Studded boots with a lightweight upper for quick movement and a secure fit.'),
    ('Goalkeeper Gloves', 'Football', 'Protective Gear', 1199, 14, 'Latex-palm gloves with finger support for a strong grip in all weather.'),
    ('Shin Guards', 'Football', 'Protective Gear', 499, 60, 'Slim, impact-absorbing shin guards with elastic straps.'),
    ('Team Football Jersey', 'Football', 'Apparel', 799, 35, 'Breathable quick-dry jersey that stays light during a full match.'),
    ('Graphite Badminton Racket', 'Badminton', 'Bats and Rackets', 1899, 22, 'Lightweight graphite racket with a balanced frame for smashes and quick drives.'),
    ('Feather Shuttlecocks (Tube of 12)', 'Badminton', 'Accessories', 1099, 30, 'Goose-feather shuttlecocks with a stable flight and a durable cork base.'),
    ('Non-Marking Court Shoes', 'Badminton', 'Footwear', 2199, 16, 'Non-marking soles for indoor courts, with extra grip for quick side steps.'),
    ('Racket Kit Bag', 'Badminton', 'Accessories', 1399, 0, 'Multi-compartment kit bag that holds up to three rackets and your shoes.'),
    ('Size 7 Basketball', 'Basketball', 'Balls', 1499, 28, 'Official-size basketball with deep channels for a better grip.'),
    ('Basketball Shoes', 'Basketball', 'Footwear', 3499, 10, 'High-top shoes with ankle support and a cushioned sole for jumping and landing.'),
    ('Sleeveless Basketball Jersey', 'Basketball', 'Apparel', 699, 45, 'Lightweight mesh jersey that keeps you cool during fast games.'),
    ('Tennis Racket', 'Tennis', 'Bats and Rackets', 3299, 9, 'Aluminium-graphite racket with a large sweet spot, good for beginners and club players.'),
    ('Tennis Balls (Can of 3)', 'Tennis', 'Balls', 499, 70, 'Pressurised tennis balls with a felt cover for a consistent bounce.'),
    ('Sports Wristbands (Pair)', 'Tennis', 'Accessories', 299, 80, 'Soft cotton wristbands that absorb sweat during long rallies.'),
    ('Adjustable Dumbbell Set', 'Fitness', 'Accessories', 2999, 8, 'A pair of adjustable dumbbells with easy-lock plates for home workouts.'),
    ('Anti-Slip Yoga Mat', 'Fitness', 'Accessories', 699, 42, '6 mm thick anti-slip yoga mat with a carry strap.'),
    ('Speed Skipping Rope', 'Fitness', 'Accessories', 249, 90, 'Adjustable-length skipping rope with smooth-rotating handles.'),
    ('Sports Water Bottle (1 L)', 'Fitness', 'Accessories', 349, 55, 'Leak-proof 1-litre bottle made of BPA-free plastic.'),
    # ---- more products ----
    ('Cricket Stumps Set with Bails', 'Cricket', 'Accessories', 899, 22, 'Set of three wooden stumps with two bails for practice matches.'),
    ('Cricket Kit Bag', 'Cricket', 'Accessories', 1599, 14, 'Large kit bag with separate pockets for the bat, pads and shoes.'),
    ('Batting Pads (Pair)', 'Cricket', 'Protective Gear', 1499, 16, 'Lightweight batting pads with soft knee roll and strong straps.'),
    ('Cricket Whites T-Shirt', 'Cricket', 'Apparel', 599, 40, 'Soft white cricket T-shirt with a breathable fabric.'),
    ('Football Socks (Pair)', 'Football', 'Apparel', 249, 70, 'Long stretchable football socks with a cushioned sole.'),
    ('Training Cones (Set of 20)', 'Football', 'Accessories', 399, 30, 'Bright cones for dribbling and agility drills.'),
    ('Football Pump with Needle', 'Football', 'Accessories', 299, 45, 'Hand pump with a needle for footballs, basketballs and volleyballs.'),
    ('Badminton Racket Grip Tape (Pack of 3)', 'Badminton', 'Accessories', 199, 80, 'Sweat-absorbing grip tape for a firm hold on the racket.'),
    ('Nylon Shuttlecocks (Tube of 6)', 'Badminton', 'Accessories', 349, 60, 'Durable nylon shuttlecocks for daily practice.'),
    ('Badminton Sports Shorts', 'Badminton', 'Apparel', 449, 33, 'Light and stretchable shorts that allow quick movement.'),
    ('Basketball Hoop Net', 'Basketball', 'Accessories', 349, 25, 'Weather-resistant nylon net that fits a standard ring.'),
    ('Basketball Air Pump', 'Basketball', 'Accessories', 249, 38, 'Compact pump to keep your ball at the right pressure.'),
    ('Basketball Arm Sleeves (Pair)', 'Basketball', 'Accessories', 399, 28, 'Compression arm sleeves that keep muscles warm.'),
    ('Tennis Overgrip (Pack of 3)', 'Tennis', 'Accessories', 299, 50, 'Tacky overgrips that improve the hold on the racket handle.'),
    ('Tennis Shoes', 'Tennis', 'Footwear', 2999, 12, 'Shoes with a strong sole and side support for quick court movement.'),
    ('Tennis Kit Bag', 'Tennis', 'Accessories', 1899, 11, 'Spacious bag that holds two rackets, balls and accessories.'),
    ('Resistance Bands Set', 'Fitness', 'Accessories', 799, 34, 'Set of five bands with different strengths for home workouts.'),
    ('Gym Gloves', 'Fitness', 'Protective Gear', 449, 40, 'Padded gloves that protect your palms during weight training.'),
    ('Push-Up Bars (Pair)', 'Fitness', 'Accessories', 549, 26, 'Non-slip push-up bars that reduce strain on the wrists.'),
    ('Running Shoes', 'Running', 'Footwear', 2599, 20, 'Lightweight running shoes with a cushioned sole and breathable mesh.'),
    ('Dry-Fit Running T-Shirt', 'Running', 'Apparel', 549, 44, 'Quick-dry T-shirt that keeps you cool on long runs.'),
    ('Running Shorts', 'Running', 'Apparel', 499, 39, 'Light shorts with an inner pocket for keys or cards.'),
    ('Running Armband for Phone', 'Running', 'Accessories', 349, 30, 'Sweat-proof armband that holds your phone while you run.'),
    ('Table Tennis Bat', 'Table Tennis', 'Bats and Rackets', 799, 25, 'Rubber-coated bat with a comfortable handle for control and spin.'),
    ('Table Tennis Balls (Pack of 6)', 'Table Tennis', 'Balls', 199, 60, '40 mm white celluloid balls for practice and matches.'),
    ('Table Tennis Shoes', 'Table Tennis', 'Footwear', 1899, 12, 'Flat-soled indoor shoes that give a good grip on wooden courts.'),
]


class Command(BaseCommand):
    help = 'Adds sample sports, categories and products so the store is not empty.'

    def handle(self, *args, **options):
        sports = {}
        for name, icon in SPORTS:
            sports[name], _ = Sport.objects.get_or_create(
                slug=slugify(name), defaults={'name': name, 'icon': icon})

        categories = {}
        for name in CATEGORIES:
            categories[name], _ = Category.objects.get_or_create(
                slug=slugify(name), defaults={'name': name})

        # Add products in a mixed order so the newest products on the home page cover several sports
        counts, keyed = {}, []
        for product in PRODUCTS:
            position = counts.get(product[1], 0)
            counts[product[1]] = position + 1
            keyed.append((position, product))
        ordered = [product for position, product in sorted(keyed, key=lambda pair: pair[0])]

        created = 0
        for name, sport, category, price, stock, description in ordered:
            _, was_created = Product.objects.get_or_create(
                slug=slugify(name),
                defaults={
                    'name': name, 'sport': sports[sport], 'category': categories[category],
                    'price': price, 'stock': stock, 'description': description,
                },
            )
            created += was_created

        self.stdout.write(self.style.SUCCESS(f'Done. {created} new products added.'))
