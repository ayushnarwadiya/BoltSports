from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from store.models import Product

EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')


class Command(BaseCommand):
    help = ('Attaches product photos from the "product_images" folder to the products. '
            'Name each photo after the product slug, for example running-shoes.jpg')

    def add_arguments(self, parser):
        parser.add_argument('--list', action='store_true',
                            help='Show the file name expected for every product')
        parser.add_argument('--overwrite', action='store_true',
                            help='Replace images that are already set')

    def handle(self, *args, **options):
        if options['list']:
            for product in Product.objects.order_by('name'):
                self.stdout.write(f'{product.slug}.jpg    <-  {product.name}')
            return

        folder = Path(settings.BASE_DIR) / 'product_images'
        folder.mkdir(exist_ok=True)
        files = {f.stem.lower(): f for f in folder.iterdir() if f.suffix.lower() in EXTENSIONS}
        slugs = set(Product.objects.values_list('slug', flat=True))

        attached = skipped = 0
        for product in Product.objects.all():
            photo = files.get(product.slug)
            if photo is None:
                continue
            if product.image and not options['overwrite']:
                skipped += 1
                continue
            with photo.open('rb') as handle:
                product.image.save(photo.name, File(handle), save=True)
            attached += 1

        for name in sorted(set(files) - slugs):
            self.stdout.write(self.style.WARNING(f'No product matches the file name: {name}'))

        without = Product.objects.filter(image='').count()
        self.stdout.write(self.style.SUCCESS(
            f'{attached} image(s) attached, {skipped} skipped (already had an image). '
            f'{without} product(s) still have no image.'))
