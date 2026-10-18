# Architecture

Django MVT: URL → view → model/template.

```
sportsstore/
  settings.py   DB (SQLite, MySQL commented), static/media, installed apps
  urls.py       includes store.urls, admin, media in DEBUG
store/
  models.py     Sport, Category, Product, Order, OrderItem
  views.py      home, about, product_list, product_detail, cart_*, checkout,
                order_success, order_history, order_detail, order_cancel, register
  urls.py       all site routes
  cart.py       session-based cart helper
  context_processors.py  cart count available in every template
  forms.py      register and checkout forms
  admin.py      admin configuration
  management/commands/  load_sample_data, attach_product_images
  templates/store/      base.html + page templates (+ _product_card, _shop_card partials)
  static/store/css/     style.css (the only stylesheet)
  static/store/js/      main.js, three.min.js, vanta.clouds2.min.js
  static/store/img/     noise.png (Vanta clouds texture)
```

## Key flows
- **Cart:** stored in the session (product id → quantity); `cart.py` builds items and totals.
- **Checkout:** login required; inside `transaction.atomic()` it validates stock, creates `Order` + `OrderItem`s (price saved at time of purchase), reduces stock, clears the cart.
- **Cancel:** allowed while status is pending/confirmed; `Order.save()` adds items back to stock once.
- **Tracking:** `Order.tracking_steps` gives the four stages with timestamps for the progress bar.
- **Home hero:** Vanta.js CLOUDS2 animates `.hero-bg`; hero product card chosen in `views.home`.

## URLs
`/` home · `/about/` · `/products/` · `/products/<slug>/` · `/cart/` (+ add/update/remove) · `/checkout/` · `/orders/` · `/orders/<id>/` (+ cancel) · `/order/success/<id>/` · `/register/` · `/login/` · `/logout/` · `/admin/`

## Deployment
PythonAnywhere: pull from GitHub, `pip install -r requirements.txt`, `collectstatic`, `migrate`, Reload.
