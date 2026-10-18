# CLAUDE.md – rules for AI assistants working on BoltSports

Read this file, then `docs/ARCHITECTURE.md`, before changing anything.

## Project
Django 5 e-commerce site (project package `sportsstore`, single app `store`). SQLite by default. Student project, so keep code simple and readable with short comments.

## Rules
- Make the smallest change that does the job. Do NOT rewrite or restyle files that were not mentioned.
- NEVER overwrite or reformat the hero section in `store/templates/store/home.html`, or `views.home` in `store/views.py` (hero product is chosen by slug `badminton-racket-grip-tape-pack-of-3`, fallback `featured[0]`). If a change touches them, show the diff and ask first.
- Do not touch `db.sqlite3` or `media/` (real products and orders live there). Never delete migrations. Model changes need `makemigrations` + `migrate`.
- Static files go through `{% static %}`; no CDN links (Vanta/three.js are local in `store/static/store/js/`).
- ALL CSS lives in ONE file: `store/static/store/css/style.css` (keep it short, no new CSS files). Reuse the variables at the top (`--ink`, `--accent`, `--paper`, `--font-display`, `--font-body`) and existing classes before writing new ones. Write simple, beginner-level CSS, like a 3rd-year student would.
- Orders: stock is reduced at checkout inside `transaction.atomic()`; cancelling restores it. Keep this behaviour.
- Payment is Cash on Delivery only.
- When asked for a change, tell me which files changed. If I will deploy to PythonAnywhere, remind me to run `collectstatic`, `migrate`, then Reload.

## Commands
`python manage.py runserver` · `makemigrations` · `migrate` · `load_sample_data` · `attach_product_images`
