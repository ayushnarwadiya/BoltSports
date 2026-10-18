# Database (SQLite by default)

| Model | Fields | Relations |
|---|---|---|
| **Sport** | name (unique), slug, icon | 1 → many Product |
| **Category** | name (unique), slug | 1 → many Product |
| **Product** | name, slug, description, price, stock, image, is_available, created_at | FK Sport, FK Category |
| **Order** | full_name, phone, address, city, pincode, payment_method (COD), total, status, created_at, confirmed_at, dispatched_at, delivered_at, cancelled_at | FK User |
| **OrderItem** | quantity, price (at purchase time) | FK Order, FK Product |

Users use Django's built-in `auth.User`.

Order status: `pending` → `confirmed` → `dispatched` → `delivered`, or `cancelled` (cannot be reopened; delivered cannot be cancelled).

Relationships: User 1–* Order 1–* OrderItem *–1 Product *–1 Sport / Category.
