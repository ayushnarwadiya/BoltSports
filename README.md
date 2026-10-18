# BoltSports

A Django e-commerce website for sports equipment, built during my Full Stack Developer (Python) internship at Clustor Computing (30 Mar – 30 May 2026).

## Features
- Home page with animated Vanta.js hero and featured product
- Shop page with sport/category filters, search and sorting
- Product detail page with stock status
- Session-based shopping cart (add, update, remove)
- User registration, login and logout
- Checkout (Cash on Delivery) with stock check
- Order history, order detail with delivery tracking bar, and order cancellation (stock is restored)
- Admin panel to manage sports, categories, products and orders
- About page

## Tech stack
Python 3, Django 5, SQLite (default; MySQL settings included, commented), HTML/CSS/JavaScript, Vanta.js + three.js (served locally), Pillow.

## Run locally
```bash
python -m venv venv
venv\Scripts\activate          # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py load_sample_data      # optional demo products
python manage.py createsuperuser       # for /admin/
python manage.py runserver
```
Open http://127.0.0.1:8000/ and the admin at http://127.0.0.1:8000/admin/.

## Project layout
```
sportsstore/   settings and root URLs
store/         the main app (models, views, urls, forms, cart, templates, static)
product_images/ optional images for the attach_product_images command
```
More detail: see `docs/ARCHITECTURE.md`, `docs/DATABASE.md`, `docs/PRD.md`.

## Using MySQL instead of SQLite
In `sportsstore/settings.py`, comment out the SQLite block and enable the MySQL block, then `pip install mysqlclient` and run `python manage.py migrate`.
