# PRD – BoltSports

## Goal
An online store where customers can browse sports equipment, add items to a cart and place Cash on Delivery orders, and an admin can manage products and orders.

## Users
- **Customer:** browses, registers, buys, tracks and cancels orders.
- **Admin:** manages catalogue and order status through Django admin.

## Features (in scope)
1. Home, About, Shop (filter by sport/category, search, sort), Product detail
2. Session cart
3. Register / login / logout
4. Checkout with delivery details, stock validation
5. Order history, tracking (Placed → Confirmed → Dispatched → Delivered), cancel while Placed/Confirmed
6. Admin management of Sport, Category, Product, Order

## Out of scope
Online payment, reviews, wishlist, email notifications, coupons.

## Success criteria
Every page works on desktop and mobile; stock never goes negative; cancelled orders restore stock.
