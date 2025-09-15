# Restaurant Management System

Python + SQLite restaurant management app with both a terminal interface and a modernized Tkinter GUI. The app auto-creates the local database and seeds a starter menu so you can run it immediately.

## Features

- Database-backed via SQLite. Schema is created automatically on first run.
- Safe, parameterized SQL everywhere (no string concatenation; `=` used for exact matches).
- Terminal CLI: manage menu, add orders, delete, update, and print receipts.
- GUI: improved professional layout, quick actions, order placement, menu management, and receipt viewer with totals.
- Auto-seeded menu (Burger, Pizza, Pasta, Salad, Soda) if menu is empty.

## Requirements

- Python 3.8+
- No external dependencies (uses stdlib `sqlite3` and `tkinter`).

## Running

- GUI (recommended):
  - `python restaurant_gui.py`
- Terminal:
  - `python restaurant_terminal.py`

On first run, `restaurant.db` is created in the project folder, schema is initialized, and a starter menu is inserted if empty.

## Notes

- Receipts group items per order and compute subtotals and a grand total.
- Write operations commit immediately; read operations are non-destructive.
- The simple schema stores one row per line item in the `customer` table, grouped by `order_id`.
